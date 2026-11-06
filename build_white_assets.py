import cv2
import numpy as np
from PIL import Image

uploaded = r'C:/Users/Dell/.gemini/antigravity/brain/cdd5fc77-ec5b-4c4d-915b-6edb1a665ae5/.user_uploaded/media_1793972397798_22175ca4.jpg'
img = cv2.imread(uploaded)
h_src, w_src = img.shape[:2]

# Center of content: X=[320, 703] (w=384), Y=[77, 479] (h=403)
# Center: cx = 512, cy = 278
cx, cy = 512, 278
half = 226
crop = img[cy-half:cy+half, cx-half:cx+half].copy()
h, w = crop.shape[:2]

# 1. Clean pure white background:
# Convert off-white [242, 248, 243] background seamlessly to pure white #ffffff
bg = img[5, 5].astype(float)
diff = np.sqrt(np.sum((crop.astype(float) - bg)**2, axis=2))
lift = np.clip((28 - diff) / 28.0, 0, 1)

crop_white = crop.copy().astype(float)
for c in range(3):
    crop_white[:, :, c] = crop_white[:, :, c] * (1.0 - lift) + 255.0 * lift
crop_white = crop_white.astype(np.uint8)

# Save pure white square version
cv2.imwrite('logo.png', crop_white)
cv2.imwrite('logo_full.png', crop_white)
cv2.imwrite('logo_white_square.png', crop_white)

# 2. Luxury Rounded White Badge for Navbar & Footer (logo_transparent.png)
# Supersample 4x for subpixel smooth corners
scale = 4
big_h, big_w = h * scale, w * scale
big_img = cv2.resize(crop_white, (big_w, big_h), interpolation=cv2.INTER_LANCZOS4)

radius = 32 * scale  # ~7% smooth corner radius
big_mask = np.zeros((big_h, big_w), dtype=np.uint8)
cv2.rectangle(big_mask, (radius, 0), (big_w - radius, big_h), 255, -1)
cv2.rectangle(big_mask, (0, radius), (big_w, big_h - radius), 255, -1)
cv2.circle(big_mask, (radius, radius), radius, 255, -1)
cv2.circle(big_mask, (big_w - radius, radius), radius, 255, -1)
cv2.circle(big_mask, (radius, big_h - radius), radius, 255, -1)
cv2.circle(big_mask, (big_w - radius, big_h - radius), radius, 255, -1)

# Subtle luxury gold border (1.5px on 1x -> 6px on 4x)
gold_bgr = [55, 175, 212]  # #d4af37 Metallic Gold
border_thick = int(1.5 * scale)
cv2.rectangle(big_img, (radius, 0), (big_w - radius, big_h), gold_bgr, border_thick)
cv2.rectangle(big_img, (0, radius), (big_w, big_h - radius), gold_bgr, border_thick)
cv2.circle(big_img, (radius, radius), radius, gold_bgr, border_thick)
cv2.circle(big_img, (big_w - radius, radius), radius, gold_bgr, border_thick)
cv2.circle(big_img, (radius, big_h - radius), radius, gold_bgr, border_thick)
cv2.circle(big_img, (big_w - radius, big_h - radius), radius, gold_bgr, border_thick)

# Downsample with anti-aliasing
smooth_badge = cv2.resize(big_img, (w, h), interpolation=cv2.INTER_AREA)
smooth_alpha = cv2.resize(big_mask, (w, h), interpolation=cv2.INTER_AREA)

badge_final = np.zeros((h, w, 4), dtype=np.uint8)
badge_final[:, :, :3] = smooth_badge
badge_final[:, :, 3] = smooth_alpha

# Save as logo_transparent.png (used in navbar & footer)
cv2.imwrite('logo_transparent.png', badge_final)
cv2.imwrite('logo_badge_white.png', badge_final)

# Also save plain white rounded without border
big_img_plain = cv2.resize(crop_white, (big_w, big_h), interpolation=cv2.INTER_LANCZOS4)
smooth_plain = cv2.resize(big_img_plain, (w, h), interpolation=cv2.INTER_AREA)
badge_plain = np.zeros((h, w, 4), dtype=np.uint8)
badge_plain[:, :, :3] = smooth_plain
badge_plain[:, :, 3] = smooth_alpha
cv2.imwrite('logo_rounded_plain.png', badge_plain)

# 3. Favicon & App Icon (Circular badge with compass emblem)
# Emblem Y=[77, 344], X=[366, 657], center = (512, 211), radius ~ 140
cx_e, cy_e = 512, 211
r_e = 145
emblem_crop = img[cy_e-r_e:cy_e+r_e, cx_e-r_e:cx_e+r_e].copy()
eh, ew = emblem_crop.shape[:2]

# Turn emblem background white
ediff = np.sqrt(np.sum((emblem_crop.astype(float) - bg)**2, axis=2))
elif_lift = np.clip((28 - ediff) / 28.0, 0, 1)
for c in range(3):
    emblem_crop[:, :, c] = (emblem_crop[:, :, c].astype(float) * (1.0 - elif_lift) + 255.0 * elif_lift).astype(np.uint8)

# Circular mask
mask_circle = np.zeros((eh, ew), dtype=np.uint8)
cv2.circle(mask_circle, (ew//2, eh//2), min(ew, eh)//2 - 2, 255, -1)

emblem_icon = cv2.cvtColor(emblem_crop, cv2.COLOR_BGR2BGRA)
emblem_icon[:, :, 3] = mask_circle

# Resize to standard icon sizes
icon_512 = cv2.resize(emblem_icon, (512, 512), interpolation=cv2.INTER_LANCZOS4)
cv2.imwrite('logo_emblem.png', icon_512)
cv2.imwrite('logo_emblem_transparent.png', icon_512)

pil_icon = Image.fromarray(cv2.cvtColor(icon_512, cv2.COLOR_BGRA2RGBA))
pil_icon.save('favicon.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

print('Generated clean white background brand assets successfully!')
