import fitz
import io
import json
import pandas as pd
from app import app

def run_tests():
    print("Testing Flask app endpoints...")

    doc = fitz.open()
    page = doc.new_page(width=842, height=595)
    page.draw_rect(fitz.Rect(20, 20, 822, 575), color=(0.2, 0.4, 0.8), width=3)
    pdf_bytes = doc.tobytes()
    doc.close()

    client = app.test_client()

    response = client.post('/api/render-preview', data={
        'name': 'Test Katılımcı Adı',
        'y_ratio': '0.62',
        'x_ratio': '0.50',
        'font_size': '84',
        'font_color': '#000000',
        'align': 'center',
        'template': (io.BytesIO(pdf_bytes), 'template.pdf')
    })

    assert response.status_code == 200, f"Preview failed: {response.data}"
    res_json = response.get_json()
    assert 'image' in res_json, "Image missing in preview response"
    print(f"OK /api/render-preview - Dimensions: {res_json['width']}x{res_json['height']}")

    excel_io = io.BytesIO()
    df = pd.DataFrame({
        "AD": ["ALİ", "MEHMET", "ZEYNEP"],
        "SOYAD": ["YILMAZ", "DEMİR", "KAYA"]
    })
    with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_io.seek(0)

    excel_resp = client.post('/api/parse-excel', data={
        'file': (excel_io, 'test.xlsx')
    })
    assert excel_resp.status_code == 200, f"Excel parse failed: {excel_resp.data}"
    excel_json = excel_resp.get_json()
    assert len(excel_json['participants']) == 3, "Expected 3 participants"
    assert excel_json['participants'][0] == "Ali Yılmaz"
    print(f"OK /api/parse-excel - Participants: {excel_json['participants']}")

    batch_resp = client.post('/api/generate-batch', data={
        'y_ratio': '0.62',
        'x_ratio': '0.50',
        'font_size': '84',
        'font_color': '#000000',
        'align': 'center',
        'template': (io.BytesIO(pdf_bytes), 'template.pdf'),
        'participants_json': json.dumps(excel_json['participants'])
    })
    assert batch_resp.status_code == 200, f"Batch generation failed: {batch_resp.data}"
    assert batch_resp.mimetype == 'application/zip', "Expected ZIP response"
    print(f"OK /api/generate-batch - ZIP size: {len(batch_resp.data)} bytes")

    index_resp = client.get('/')
    assert index_resp.status_code == 200, "Index page failed"
    html = index_resp.get_data(as_text=True)
    assert 'canvas-container' in html
    assert 'drag-handle' in html
    print("OK GET / - Index page rendered")

    print("All tests passed!")

if __name__ == "__main__":
    run_tests()