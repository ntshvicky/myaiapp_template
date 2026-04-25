from PIL import Image, ImageChops, ImageStat


class ImageCompareService:
    def compare(self, image1, image2):
        with Image.open(image1) as img_a, Image.open(image2) as img_b:
            img_a = img_a.convert("RGB").resize((512, 512))
            img_b = img_b.convert("RGB").resize((512, 512))
            diff = ImageChops.difference(img_a, img_b)
            stat = ImageStat.Stat(diff)
            rms = sum(value ** 2 for value in stat.rms) ** 0.5
            similarity = max(0.0, min(1.0, 1.0 - (rms / 441.67295593)))
        return {"score": round(similarity, 4), "diff_url": ""}
