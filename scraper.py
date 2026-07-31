import os
import re
import urllib.request
from urllib.parse import urljoin, urlparse

SITE_URL = "https://www.dpivisual.com.br"
OUTPUT_DIR = os.path.join(".", "src", "images")

def setup_folder():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def baixar_asset(url, caminho_destino):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            dados = response.read()
            if len(dados) > 0:
                with open(caminho_destino, "wb") as f:
                    f.write(dados)
                print(f"✅ Baixado: {caminho_destino}")
                return True
    except Exception as e:
        print(f"⚠️ Erro ao baixar {url}: {e}")
    return False

def executar_scraping():
    setup_folder()
    print(f"🔎 Buscando assets em {SITE_URL}...")
    
    logo_baixada = False

    try:
        req = urllib.request.Request(
            SITE_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")

        # Procura por imagens com termos de logo
        img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
        for src in img_matches:
            if any(k in src.lower() for k in ["logo", "dpi", "brand", "header"]):
                full_url = urljoin(SITE_URL, src)
                ext = os.path.splitext(urlparse(full_url).path)[1] or ".png"
                destino = os.path.join(OUTPUT_DIR, f"logo{ext}")
                if baixar_asset(full_url, destino):
                    logo_baixada = True
                    break

        # Fallback para OpenGraph
        if not logo_baixada:
            og_match = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if og_match:
                full_url = urljoin(SITE_URL, og_match.group(1))
                destino = os.path.join(OUTPUT_DIR, "logo.png")
                baixar_asset(full_url, destino)

        # Favicon
        fav_match = re.search(r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if fav_match:
            full_url = urljoin(SITE_URL, fav_match.group(1))
            destino = os.path.join(OUTPUT_DIR, "favicon.ico")
            baixar_asset(full_url, destino)

        print("\n✨ Download finalizado! Confira os arquivos em src/images/")

    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    executar_scraping()