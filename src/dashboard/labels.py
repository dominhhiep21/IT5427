"""Nhãn tiếng Việt cho các giá trị dữ liệu gốc: danh mục hàng và nhãn mô hình.

Giá trị gốc (tiếng Bồ Đào Nha) vẫn là khoá dùng trong SQL; ở đây chỉ đổi chữ hiển thị.
"""

from __future__ import annotations

import unicodedata

UNKNOWN = "Không xác định"

CATEGORY_LABELS_VI = {
    "agro_industria_e_comercio": "Nông nghiệp, công nghiệp & thương mại",
    "alimentos": "Thực phẩm",
    "alimentos_bebidas": "Thực phẩm & đồ uống",
    "artes": "Nghệ thuật",
    "artes_e_artesanato": "Nghệ thuật & thủ công",
    "artigos_de_festas": "Đồ dùng tiệc & lễ hội",
    "artigos_de_natal": "Đồ trang trí Giáng sinh",
    "audio": "Âm thanh",
    "automotivo": "Phụ tùng ô tô",
    "bebes": "Đồ cho bé",
    "bebidas": "Đồ uống",
    "beleza_saude": "Sức khỏe & làm đẹp",
    "brinquedos": "Đồ chơi",
    "cama_mesa_banho": "Chăn ga gối & phòng tắm",
    "casa_conforto": "Tiện nghi gia đình",
    "casa_conforto_2": "Tiện nghi gia đình (bộ 2)",
    "casa_construcao": "Vật liệu xây dựng",
    "cds_dvds_musicais": "CD & DVD âm nhạc",
    "cine_foto": "Máy ảnh & quay phim",
    "climatizacao": "Điều hòa & thông gió",
    "consoles_games": "Máy chơi game & phụ kiện",
    "construcao_ferramentas_construcao": "Dụng cụ xây dựng",
    "construcao_ferramentas_ferramentas": "Dụng cụ cầm tay",
    "construcao_ferramentas_iluminacao": "Thiết bị chiếu sáng",
    "construcao_ferramentas_jardim": "Dụng cụ làm vườn",
    "construcao_ferramentas_seguranca": "Thiết bị an toàn lao động",
    "cool_stuff": "Đồ độc lạ",
    "dvds_blu_ray": "DVD & Blu-ray",
    "eletrodomesticos": "Đồ điện gia dụng",
    "eletrodomesticos_2": "Đồ điện gia dụng (bộ 2)",
    "eletronicos": "Điện tử",
    "eletroportateis": "Đồ điện cầm tay",
    "esporte_lazer": "Thể thao & giải trí",
    "fashion_bolsas_e_acessorios": "Túi xách & phụ kiện thời trang",
    "fashion_calcados": "Giày dép thời trang",
    "fashion_esporte": "Đồ thể thao thời trang",
    "fashion_roupa_feminina": "Quần áo nữ",
    "fashion_roupa_infanto_juvenil": "Quần áo trẻ em",
    "fashion_roupa_masculina": "Quần áo nam",
    "fashion_underwear_e_moda_praia": "Đồ lót & đồ đi biển",
    "ferramentas_jardim": "Dụng cụ làm vườn",
    "flores": "Hoa",
    "fraldas_higiene": "Tã & đồ vệ sinh",
    "industria_comercio_e_negocios": "Công nghiệp, thương mại & kinh doanh",
    "informatica_acessorios": "Phụ kiện máy tính",
    "instrumentos_musicais": "Nhạc cụ",
    "la_cuisine": "Đồ bếp cao cấp",
    "livros_importados": "Sách nhập khẩu",
    "livros_interesse_geral": "Sách phổ thông",
    "livros_tecnicos": "Sách kỹ thuật",
    "malas_acessorios": "Vali & phụ kiện",
    "market_place": "Sàn thương mại điện tử",
    "moveis_colchao_e_estofado": "Nội thất, đệm & ghế sofa",
    "moveis_cozinha_area_de_servico_jantar_e_jardim": "Nội thất bếp, phòng ăn & sân vườn",
    "moveis_decoracao": "Nội thất trang trí",
    "moveis_escritorio": "Nội thất văn phòng",
    "moveis_quarto": "Nội thất phòng ngủ",
    "moveis_sala": "Nội thất phòng khách",
    "musica": "Âm nhạc",
    "papelaria": "Văn phòng phẩm",
    "pc_gamer": "Máy tính chơi game",
    "pcs": "Máy tính",
    "perfumaria": "Nước hoa",
    "pet_shop": "Đồ cho thú cưng",
    "portateis_casa_forno_e_cafe": "Lò nướng & máy pha cà phê",
    "portateis_cozinha_e_preparadores_de_alimentos": "Máy chế biến thực phẩm",
    "relogios_presentes": "Đồng hồ & quà tặng",
    "seguros_e_servicos": "Bảo hiểm & dịch vụ",
    "sinalizacao_e_seguranca": "Biển báo & thiết bị an toàn",
    "tablets_impressao_imagem": "Máy tính bảng, in ấn & hình ảnh",
    "telefonia": "Điện thoại",
    "telefonia_fixa": "Điện thoại cố định",
    "unknown": UNKNOWN,
    "utilidades_domesticas": "Đồ dùng trong nhà",
}

TARGET_LABELS_VI = {"is_late": "đơn giao trễ"}


def _fallback(value: str) -> str:
    """Giá trị lạ: đổi gạch dưới thành khoảng trắng và viết hoa chữ đầu, không bịa nghĩa."""

    words = value.replace("_", " ").strip()
    return words[:1].upper() + words[1:] if words else value


def category_label(value: str) -> str:
    """Nhãn tiếng Việt của một danh mục; giá trị lạ rơi về dạng đọc được của chính nó."""

    return CATEGORY_LABELS_VI.get(value, _fallback(value))


def target_label(value: str) -> str:
    """Nhãn tiếng Việt của cột đích; giá trị lạ giữ nguyên."""

    return TARGET_LABELS_VI.get(value, value)


def sort_key(text: str) -> str:
    """Khoá sắp xếp bỏ dấu, để "Bảo" đứng trước "Biển" như tiếng Việt."""

    decomposed = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    return "".join(char for char in decomposed if not unicodedata.combining(char)).lower()
