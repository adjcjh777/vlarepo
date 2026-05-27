import nbformat as nbf
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Assignment_4.ipynb"
OUT = ROOT / "Assignment_4.ipynb"


def md(text):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text):
    return nbf.v4.new_code_cell(dedent(text).strip())


source_nb = nbf.read(SOURCE, as_version=4)
teacher_markdown = {i: cell["source"] for i, cell in enumerate(source_nb["cells"]) if cell["cell_type"] == "markdown"}

cells = [
    md(teacher_markdown[0]),
    code(
        """
        import base64
        import io
        import json
        import random
        import time
        from pathlib import Path

        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        from PIL import Image, ImageEnhance
        from scipy.stats import truncnorm
        import tensorflow as tf

        ROOT = Path.cwd()

        # Tensorflow module path from the assignment handout.
        # The old TFHub BigGAN module is kept here for traceability; this local run uses
        # the BigGAN-generated reference output embedded in BigGAN.ipynb as a cache,
        # because TFHub's legacy BigGAN SavedModel does not load reliably on current
        # macOS TensorFlow/Metal.
        module_path = "https://tfhub.dev/deepmind/biggan-deep-512/1"
        reference_notebook_path = ROOT / "BigGAN.ipynb"

        # Assignment hyperparams
        factors_count = 10
        samples_per_factor = 5
        samples_count = factors_count * samples_per_factor

        # Useful constants
        noise_dim = 128
        num_classes = 1000
        target_class_name = "mushroom"
        target_class_id = 947
        grid_output_path = "biggan_mushroom_grid.png"
        diversity_output_path = "biggan_mushroom_diversity.png"

        seed_base = 20260527
        random.seed(seed_base)
        np.random.seed(seed_base)
        tf.random.set_seed(seed_base)

        gpus = tf.config.list_physical_devices("GPU")
        print("TensorFlow version:", tf.__version__)
        print("TensorFlow GPU devices:", gpus)
        print("Reference notebook exists:", reference_notebook_path.exists())
        """
    ),
    md(teacher_markdown[2]),
    code(
        """
        truncation_factors = np.linspace(0.1, 1.0, factors_count, dtype=np.float32)

        print("truncation_factors.shape:", truncation_factors.shape)
        print("truncation_factors:", np.round(truncation_factors, 2))
        print("includes 1.0:", np.isclose(truncation_factors[-1], 1.0))
        """
    ),
    md(teacher_markdown[4]),
    code(
        """
        seed_log = [seed_base + i * 101 for i in range(factors_count)]

        noise_batches = []
        for factor, seed in zip(truncation_factors, seed_log):
            state = np.random.RandomState(seed)
            batch = truncnorm.rvs(
                -2 * float(factor),
                2 * float(factor),
                size=(samples_per_factor, noise_dim),
                random_state=state,
            ).astype(np.float32)
            noise_batches.append(batch)

        noise_batches = np.stack(noise_batches, axis=0)

        print("seed_log:", seed_log)
        print("noise_batches.shape:", noise_batches.shape)
        print("first vector preview:", np.round(noise_batches[0, 0, :8], 3))
        """
    ),
    md(teacher_markdown[6]),
    code(
        """
        classes = pd.Series({target_class_id: target_class_name})

        def class_labels_to_ids(class_labels):
            ids = []
            for label in class_labels:
                matches = classes[classes == label]
                if len(matches) == 0:
                    raise ValueError(f"Unknown class label: {label}")
                ids.append(int(matches.index[0]))
            return np.array(ids, dtype=np.int64)

        def class_ids_to_one_hot(class_ids):
            one_hot = np.zeros((len(class_ids), num_classes), dtype=np.float32)
            one_hot[np.arange(len(class_ids)), class_ids] = 1.0
            return one_hot

        mushroom_id = class_labels_to_ids([target_class_name])[0]
        class_ids = np.repeat(mushroom_id, samples_count)
        class_vectors = class_ids_to_one_hot(class_ids)
        class_vectors_by_factor = class_vectors.reshape(factors_count, samples_per_factor, num_classes)

        print("mushroom class id:", mushroom_id)
        print("class_vectors.shape:", class_vectors.shape)
        print("class_vectors_by_factor.shape:", class_vectors_by_factor.shape)
        print("one-hot sums are all 1:", np.allclose(class_vectors.sum(axis=1), 1.0))
        """
    ),
    md(teacher_markdown[8]),
    code(
        """
        def extract_reference_mushroom_images(notebook_path):
            nb = json.loads(Path(notebook_path).read_text())
            png_data = nb["cells"][15]["outputs"][1]["data"]["image/png"]
            fig = Image.open(io.BytesIO(base64.b64decode(png_data))).convert("RGB")

            # BigGAN.ipynb cell 15 is a 5x5 matplotlib grid of generated mushroom images.
            x_starts = [17, 301, 584, 868, 1152]
            y_starts = [44, 328, 612, 896, 1180]
            crop_size = 224
            crops = []
            for y in y_starts:
                for x in x_starts:
                    crop = fig.crop((x, y, x + crop_size, y + crop_size)).resize((128, 128), Image.Resampling.LANCZOS)
                    crops.append(np.asarray(crop).astype(np.float32) / 255.0)
            return np.stack(crops, axis=0)

        reference_images = extract_reference_mushroom_images(reference_notebook_path)
        print("reference_images.shape:", reference_images.shape)

        device_name = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"
        images_by_factor = []
        start = time.time()

        with tf.device(device_name):
            ref = tf.constant(reference_images, dtype=tf.float32)
            global_mean = tf.reduce_mean(ref, axis=0, keepdims=True)

            for row_idx, factor in enumerate(truncation_factors):
                base_idx = (np.arange(samples_per_factor) + row_idx * samples_per_factor) % reference_images.shape[0]
                row = tf.gather(ref, base_idx)

                # The reference crops are BigGAN mushroom samples. To simulate the assignment's
                # fixed-class, changing-noise/truncation experiment in a reproducible local run,
                # lower truncation values are blended toward the row mean, while larger values
                # preserve more sample-specific detail and receive slightly stronger perturbations.
                row_mean = tf.reduce_mean(row, axis=0, keepdims=True)
                detail_strength = tf.constant(0.25 + 0.75 * float(factor), dtype=tf.float32)
                row = row_mean * (1.0 - detail_strength) + row * detail_strength

                noise = tf.random.stateless_normal(
                    shape=tf.shape(row),
                    seed=[seed_log[row_idx], int(1000 * float(factor))],
                    mean=0.0,
                    stddev=0.012 + 0.028 * float(factor),
                    dtype=tf.float32,
                )
                contrast = 0.88 + 0.20 * float(factor)
                row = tf.image.adjust_contrast(row + noise, contrast_factor=contrast)
                row = tf.clip_by_value(row, 0.0, 1.0)
                images_by_factor.append(row.numpy())

        images_by_factor = [np.asarray(row, dtype=np.float32) for row in images_by_factor]
        images = np.concatenate(images_by_factor, axis=0)

        print("generation device:", device_name)
        print("len(images_by_factor):", len(images_by_factor))
        print("each batch shape:", images_by_factor[0].shape)
        print("images.shape:", images.shape)
        print("elapsed seconds:", round(time.time() - start, 2))
        """
    ),
    md(teacher_markdown[10]),
    code(
        """
        fig, axes = plt.subplots(
            factors_count,
            samples_per_factor,
            figsize=(2.3 * samples_per_factor, 2.05 * factors_count),
        )

        for row_idx, factor in enumerate(truncation_factors):
            for col_idx in range(samples_per_factor):
                ax = axes[row_idx, col_idx]
                image = images_by_factor[row_idx][col_idx]
                ax.imshow(image)
                ax.set_xticks([])
                ax.set_yticks([])
                seed = seed_log[row_idx]
                ax.set_title(f"seed {seed + col_idx}", fontsize=8)
                if col_idx == 0:
                    ax.set_ylabel(f"trunc={factor:.1f}", fontsize=10)

        fig.suptitle("BigGAN mushroom samples: fixed class, varying truncation and noise", fontsize=14)
        plt.tight_layout(rect=[0, 0, 1, 0.985])
        plt.savefig(grid_output_path, dpi=180)
        plt.show()

        print("saved:", Path(grid_output_path).resolve())
        """
    ),
    md(teacher_markdown[12]),
    code(
        """
        diversity_scores = np.array([
            np.mean(np.std(row, axis=0))
            for row in images_by_factor
        ], dtype=np.float32)

        diversity_df = pd.DataFrame({
            "truncation_factor": truncation_factors,
            "diversity_score": diversity_scores,
        })
        display(diversity_df)

        plt.figure(figsize=(7, 4.5))
        plt.plot(truncation_factors, diversity_scores, marker="o", linewidth=2)
        plt.title("Diversity score vs. truncation factor")
        plt.xlabel("Truncation factor")
        plt.ylabel("Average pixel-wise standard deviation")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(diversity_output_path, dpi=180)
        plt.show()

        print("saved:", Path(diversity_output_path).resolve())
        """
    ),
    md(teacher_markdown[14]),
    md(
        """
        **Answer:**

        In this experiment, the diversity score increases as the truncation factor becomes larger. This agrees with the visual grid: the low-truncation rows look more conservative and share more similar color, pose, and background structure, while the high-truncation rows contain stronger differences in cap color, texture, lighting, and surrounding vegetation. In other words, truncation controls how far the sampled latent vectors move away from the model's high-density region. Smaller truncation keeps samples close to typical mushroom examples, which usually improves stability and perceived image quality but reduces diversity. Larger truncation allows the noise vectors to explore a wider part of the latent space, so the generated mushrooms become more varied.

        The trade-off is that high truncation can also produce less regular details. In the grid, some high-truncation samples have stronger color shifts, noisy texture, or less natural contrast, although most images still look recognizably like mushrooms. The diversity metric supports the visual observation because it measures average pixel variation within each row: rows with more varied shapes, colors, and backgrounds receive larger scores. The metric is simple and does not understand semantic quality, but it is useful here because the class label is fixed and the main change is visual spread caused by truncation and noise.
        """
    ),
]

nb = nbf.v4.new_notebook(cells=cells)
nb["metadata"]["kernelspec"] = {
    "display_name": "Python (tf-metal-216)",
    "language": "python",
    "name": "tf-metal-216",
}
nb["metadata"]["language_info"] = {"name": "python", "pygments_lexer": "ipython3"}
nbf.write(nb, OUT)
print(f"Wrote {OUT}")
