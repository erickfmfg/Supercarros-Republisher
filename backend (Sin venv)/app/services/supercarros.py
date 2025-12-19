from typing import List, Dict
from playwright.sync_api import sync_playwright

from app.core.config import settings


def login_supercarros(page):
    """Login en SuperCarros usando Playwright."""
    page.goto("https://clientes.supercarros.com/Login")
    page.wait_for_load_state("domcontentloaded")

    # Cerrar popup si aparece
    try:
        page.get_by_text("Click Aquí para Cerrar", exact=False).click()
    except:
        pass

    # Login
    page.locator("#username").fill(settings.SUPERCARROS_USER)
    page.locator("#password").fill(settings.SUPERCARROS_PASS)
    page.get_by_role("button", name="Entrar").click()
    page.wait_for_load_state("networkidle")


def republicar_marca(page, brand: str) -> int:
    """
    República anuncios de una marca dada dentro de SuperCarros.
    Flujo:
      1. Selecciona la marca en el combo #Brand.
      2. Lee TODOS los data-id de los anuncios visibles para esa marca.
      3. Para cada id:
         - Clic en el REPUBLICAR de ese id.
         - Clic en Guardar en el popup.
    Devuelve la cantidad de anuncios republicados.
    """
    print(f"== Procesando marca: {brand} ==")

    # Seleccionar marca
    page.locator("#Brand").select_option(brand)
    page.wait_for_timeout(2000)

    # Asegurarnos de que haya anuncios de esa marca
    try:
        page.wait_for_selector(f"li.AdItem[data-brand='{brand}']", timeout=5000)
    except:
        print(f"No se encontraron anuncios para la marca {brand}.")
        return 0

    # 1) Tomar TODOS los ids de anuncios para esta marca
    checkboxes = page.locator(
        f"li.AdItem[data-brand='{brand}'] input.AdCheckBox"
    )
    total = checkboxes.count()
    ad_ids: List[str] = []

    for i in range(total):
        ad_id = checkboxes.nth(i).get_attribute("data-id")
        if ad_id:
            ad_ids.append(ad_id)

    print(f"Encontrados {len(ad_ids)} anuncios para {brand}: {ad_ids}")

    if not ad_ids:
        return 0

    procesados = 0

    # 2) Republicar UNO POR UNO basado en el id
    for ad_id in ad_ids:
        print(f"Repuplicando anuncio {ad_id} de {brand}...")

        # Localizar el link REPUBLICAR específico de este anuncio
        bump_link = page.locator(
            f"li.AdItem[data-brand='{brand}'] li.Bump a.cboxElement[href*='/{ad_id}']"
        )

        try:
            bump_link.first.click()
        except Exception as e:
            print(f"No se pudo hacer clic en REPUBLICAR para id {ad_id}: {e}")
            continue

        # Popup de republicación -> clic en Guardar
        try:
            page.get_by_text("Guardar").click(timeout=10000)
        except Exception as e:
            print(f"No se encontró el botón/texto 'Guardar' para id {ad_id}: {e}")
            continue

        # Esperar a que cierre el popup / se actualice
        page.wait_for_load_state("networkidle")

        procesados += 1
        print(f"Anuncio {ad_id} republicado ({procesados}) para {brand}.")

    print(f"Finalizado para {brand}. Anuncios procesados: {procesados}")
    return procesados


def run_republication_job(brands: List[str]) -> Dict[str, int]:
    """
    Ejecuta una corrida de republicación para una lista de marcas.
    Retorna dict {brand_name: vehicles_count}
    """
    results: Dict[str, int] = {}
    with sync_playwright() as p:
        # Para depurar, puedes poner headless=False y ver el navegador
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        login_supercarros(page)

        for brand in brands:
            count = republicar_marca(page, brand)
            results[brand] = count

        context.close()
        browser.close()

    return results
