
import cv2
import numpy as np

def order_points(pts):
    pts = pts.reshape(4,2).astype('float32')
    s = pts.sum(axis=1)
    d = np.diff(pts,axis=1)
    return np.array([
        pts[np.argmin(s)],
        pts[np.argmin(d)],
        pts[np.argmax(s)],
        pts[np.argmax(d)]
    ])

def four_point_warp(img, pts): 
    rect = order_points(pts)
    tl, tr, br, bl = rect
    w = int(max(np.linalg.norm(tr-tl), np.linalg.norm(br - bl)))
    h = int(max(np.linalg.norm(tr-br), np.linalg.norm(tl - bl)))
    dst = np.array([ [0,0], [w-1,0], [w-1,h-1], [0,h-1]]).astype('float32')
    M = cv2.getPerspectiveTransform(rect,dst)
    return cv2.warpPerspective(img,M,(w,h))

def canny(img):
    area = img.shape[0] * img.shape[1]
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray,(5,5),0)
    edged = cv2.Canny(blurred,50,150)
    edged = cv2.dilate(edged,np.ones((3,3),np.uint8),iterations=1)
    return edged, area

def find_document_contours(edged, orig_area):
    contours, _ = cv2.findContours(edged,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours,key=cv2.contourArea, reverse=True)[:10]
    for c in contours: 
        if cv2.contourArea(c) < orig_area * 0.15:
            continue
        peri = cv2.arcLength(c,True)
        approx = cv2.approxPolyDP(c,0.02*peri,True)
        if len(approx)==4:
            return approx
    return None

#Pipeline 

def document_scanner(img_path, out_path = 'scanned.jpg'):
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {img_path}")

    orig = img.copy()
    orig_h, orig_w = orig.shape[:2]
    target_h = 900
    ratio = target_h / float(orig_h)

    resized = cv2.resize(orig,(int(orig_w*ratio),target_h))
    edged, area = canny(resized)
    approx = find_document_contours(edged,area)

    if approx is None:
            print("Cannot find the document, use the whole image")
            h, w = resized.shape[:2]
            approx = np.array([[[0, 0]], [[w - 1, 0]], [[w - 1, h - 1]], [[0, h - 1]]])

    pts_original = approx.reshape(4,2).astype('float32') / ratio
    warped = four_point_warp(orig,pts_original)

    cv2.imwrite(out_path,warped)

def make_warped_document(
    width=800,
    height=600,
    doc_width=300,
    doc_height=400,
    seed=42
):
    rng = np.random.default_rng(seed)

    # Create a dark background
    img = np.full((height, width, 3), 80, dtype=np.uint8)

    # Create a synthetic document
    doc = np.full((doc_height, doc_width, 3), 245, dtype=np.uint8)

    # Document title
    cv2.putText(
        doc, "MY DOCUMENT", (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2
    )

    # Simulate text lines
    for y in range(80, doc_height - 20, 35):
        cv2.line(doc, (20, y), (doc_width - 20, y), (130, 130, 130), 2)

    # Original document corners: TL, TR, BR, BL
    src = np.array([
        [0, 0],
        [doc_width - 1, 0],
        [doc_width - 1, doc_height - 1],
        [0, doc_height - 1]
    ], dtype=np.float32)

    # Randomly generate a perspective-distorted quadrilateral
    margin = 40
    dst = np.array([
        [rng.integers(margin, width // 2),
         rng.integers(margin, height // 3)],
        [rng.integers(width // 2, width - margin),
         rng.integers(margin, height // 3)],
        [rng.integers(width // 2, width - margin),
         rng.integers(height // 2, height - margin)],
        [rng.integers(margin, width // 2),
         rng.integers(height // 2, height - margin)]
    ], dtype=np.float32)

    # Warp document onto the background
    M = cv2.getPerspectiveTransform(src, dst)
    warped_doc = cv2.warpPerspective(doc, M, (width, height))

    # Create a mask for the document area
    mask_src = np.full((doc_height, doc_width), 255, dtype=np.uint8)
    mask = cv2.warpPerspective(mask_src, M, (width, height))

    # Place document onto the background
    img[mask > 0] = warped_doc[mask > 0]
    cv2.imwrite('test-img.jpg',img)
    
    

make_warped_document()
img_path = 'test-img.jpg'
document_scanner(img_path)
    
