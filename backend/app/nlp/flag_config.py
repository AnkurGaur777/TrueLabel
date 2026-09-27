ALLERGEN_KEYWORDS = {
    "milk": ["milk", "lactose", "whey", "casein", "butter", "lait", "milch", "leche"],
    "eggs": ["egg", "albumin", "oeuf", "ei ", "huevo"],
    "peanuts": ["peanut", "groundnut", "arachide", "erdnuss", "cacahuete"],
    "tree_nuts": ["almond", "cashew", "walnut", "hazelnut", "pistachio", "pecan", "noisette", "amande", "haselnuss", "mandel", "almendra", "avellana"],
    "soy": ["soy", "soya", "soja"],
    "wheat_gluten": ["wheat", "gluten", "barley", "rye", "ble", "blé", "weizen", "trigo", "orge", "gerste", "cebada"],
    "fish": ["fish", "anchovy", "salmon", "tuna", "poisson", "fisch", "pescado"],
    "shellfish": ["shrimp", "crab", "lobster", "shellfish", "crevette", "crabe"],
    "sesame": ["sesame", "sesamo", "sésame"],
}

ARTIFICIAL_ADDITIVE_KEYWORDS = [
    "artificial flavor", "artificial flavour", "artificial color", "artificial colour",
    "msg", "monosodium glutamate", "glutamate monosodique",
    "aspartame", "sucralose", "acesulfame",
    "sodium benzoate", "potassium sorbate", "bha", "bht", "tbhq",
    "high fructose corn syrup", "hydrogenated oil", "partially hydrogenated",
    "colorant", "farbstoff", "arome artificiel", "arôme artificiel",
]

HIGH_SUGAR_INDICATORS = [
    "sugar", "corn syrup", "glucose syrup", "fructose", "dextrose",
    "cane sugar", "maltose", "sucrose", "honey", "molasses", "syrup",
    "sucre", "zucker", "azucar", "azúcar", "sirop", "sirup",
    "miel", "honig",
]

ULTRA_PROCESSED_MARKERS = [
    "emulsifier", "stabilizer", "stabiliser", "thickener", "preservative",
    "artificial", "modified starch", "hydrolyzed", "hydrolysed",
    "flavor enhancer", "flavour enhancer",
    "emulgator", "emulsifiant", "conservateur", "conservante",
    "exhausteur de gout", "exhausteur de goût",
]
