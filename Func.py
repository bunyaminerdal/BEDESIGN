from decimal import Decimal, ROUND_HALF_UP
import math

def format_gosterilecek_sayi(sayi) -> str:
    d = Decimal(str(sayi))
    sonuc = ""
    # 1'den büyük veya -1'den küçükse → 3 basamak
    if d > 1 or d < -1:
        sonuc = str(d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))
        return str(sonuc)

    if d == 0:
        sonuc = "0"
        return str(sonuc)

    # Virgülden sonra ilk sıfır olmayan rakamın pozisyonunu bul
    # Örnek: 0.00102 → log10 ≈ -3, sıfır sayısı = 2
    log_val = math.floor(math.log10(float(abs(d))))
    sifir_sayisi = -log_val - 1       # baştaki sıfır adedi
    toplam_basamak = sifir_sayisi + 3  # sıfırlar + 3 anlamlı basamak

    quantize_str = "0." + "0" * toplam_basamak
    result = d.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

    # Sondaki gereksiz sıfırları temizle: 0.500 → 0.5
    result_str = str(result)
    if "." in result_str:
        result_str = result_str.rstrip("0").rstrip(".")

    sonuc = (result_str)
    return str(sonuc)
