"""Key farming guides bundled inside the app. They need NO internet and NO AI call, so they keep working on a weak
connection, and they are included in the downloadable offline pack. Deliberately general and safe: no chemical doses.
"""
GUIDES = {
    "safe_spray": {"title": "Using pesticides safely", "tags": "pests safety", "steps": [
        "Try low-risk options first: remove affected leaves, hand-pick pests, use traps, neem-based products.",
        "Only use a product that is approved for your crop in your country. Read the whole label before you buy and before you use it.",
        "Wear gloves, long sleeves, boots, a face covering and eye protection when mixing and spraying.",
        "Spray in the early morning or evening, in calm weather. Never spray into the wind or just before rain.",
        "Keep children, animals and food away. Never store chemicals in drink bottles.",
        "Wash your hands and clothes after spraying. Triple-rinse empty containers and dispose of them as your local rules say.",
        "Respect the waiting time on the label between spraying and harvest.",
        "If someone feels sick after contact, move to fresh air, remove contaminated clothes and get medical help. Take the label with you."]},
    "soil_test": {"title": "Understanding a soil test", "tags": "soil fertilizer", "steps": [
        "A soil test tells you pH (how acidic or alkaline the soil is) and which nutrients are low, medium or high.",
        "Most crops grow best around pH 6 to 7. Very acid soil can be improved with organic matter and, if advised, lime. Very alkaline soil may need organic matter and gypsum as advised.",
        "Take samples from 8 to 10 spots in a field, mix them, and send about half a kilogram to a soil lab.",
        "Sample before planting, and not right after fertilizer or manure has been applied.",
        "Use the lab's crop-wise advice. Ask your local agriculture office or KVK if the numbers are unclear.",
        "Test every 2 to 3 years, or when a field gives poor yields without a clear reason."]},
    "water_saving": {"title": "Saving water on the farm", "tags": "water irrigation", "steps": [
        "Mulch the soil with straw, leaves or crop residue to reduce evaporation.",
        "Water in the early morning or evening, directly at the roots, instead of in the heat of the day.",
        "Check the soil first: push a finger about 5 cm down. If it is damp, wait.",
        "Drip or furrow irrigation uses much less water than flooding for most vegetables and orchards.",
        "Add compost to help sandy soil hold water and heavy soil drain better.",
        "Catch rainwater from roofs or build small bunds and ponds to hold runoff.",
        "In dry areas, choose crops and varieties that tolerate drought, such as millets and pulses."]},
    "compost": {"title": "Making compost", "tags": "soil organic", "steps": [
        "Mix 'green' material (vegetable waste, fresh leaves, manure) with 'brown' material (dry leaves, straw).",
        "Build a heap or pit about 1 metre wide, in the shade if possible. Do not add meat, oil or diseased plants.",
        "Keep it as damp as a squeezed sponge. Cover it to hold the moisture.",
        "Turn it every 2 to 3 weeks to give it air and speed up the process.",
        "It is ready in about 2 to 4 months, when it is dark, crumbly and smells like forest soil.",
        "Spread it on the field or mix it into planting holes before sowing."]},
    "ipm": {"title": "Integrated pest management (IPM)", "tags": "pests organic", "steps": [
        "Prevent first: healthy soil, clean seed, good spacing, and crop rotation.",
        "Walk your field every week. Check the underside of leaves and note what you find.",
        "Know the pest before you act: many insects in your field are helpers (ladybirds, spiders, bees).",
        "Use simple controls first: pick off pests, traps, resistant varieties, neem products.",
        "Use stronger products only if damage passes the level your local adviser gives, and follow the label.",
        "Rotate crops and clean up crop residues after harvest to break the pest cycle."]},
    "rotation": {"title": "Crop rotation basics", "tags": "soil organic", "steps": [
        "Do not grow the same crop, or crops from the same family, in the same field year after year.",
        "Follow a hungry crop (maize, rice, vegetables) with a soil-building one (beans, groundnut, other legumes).",
        "Legumes add nitrogen to the soil, which saves fertilizer for the next crop.",
        "Mix deep-rooted and shallow-rooted crops to use different layers of soil.",
        "Keep a simple record of what grew where. Your farm journal in AgroNova can do this."]},
    "storage": {"title": "Storing grain safely", "tags": "harvest storage", "steps": [
        "Dry grain well before storage. Grain that snaps instead of bending is usually dry enough.",
        "Clean the store and remove old grain, dust and broken kernels before adding new grain.",
        "Use clean, dry bags or sealed containers. Keep them off the floor and away from walls.",
        "Keep the store cool, dry and closed to rats and insects.",
        "Check stored grain every 2 weeks for heat, mould, a musty smell or insects.",
        "Do not mix new grain with old grain."]},
    "weather_safety": {"title": "Heat, flood and frost: simple actions", "tags": "weather safety", "steps": [
        "Heat: water in the cool hours, mulch the soil, avoid hard work at midday, and drink plenty of water yourself.",
        "Heavy rain or flood: clear drainage channels, harvest ripe crops early if possible, and keep seed and stored crops dry.",
        "Frost: cover young plants in the evening, water the soil lightly before a cold night, and avoid pruning in cold spells.",
        "Storm: stay out of open fields, move animals to shelter, and secure tools and covers.",
        "After extreme weather, check plants for damage and disease over the following week."]},
}


def guide_ids() -> list:
    return list(GUIDES)
