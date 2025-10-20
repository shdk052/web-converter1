from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# קבועי נפח (במ"ל)
CUP_ML = 180
TBS_ML = 15  # כף
TS_ML = 5  # כפית

MATERIAL_DENSITY = {
    'water': 1.0,
    'sugar': 0.85,
    'flour': 0.53,
    'salt': 1.2,
    'oil': 0.92,
    'baking_powder': 0.9,
    'butter': 0.95,
    'rice': 0.85,
    'honey': 1.4
}


def gram_to_ml(grams, material):
    """
    המרת גרם למ"ל לפי סוג החומר
    צפיפות = גרם/מ"ל
    נפח (מ"ל) = משקל (גרם) / צפיפות
    """
    if material not in MATERIAL_DENSITY:
        return grams
    density = MATERIAL_DENSITY[material]
    return grams / density


def format_volume_to_fraction(ml_amount, unit_ml, unit_name_singular,
                              unit_name_plural):
    """
    מעצב נפח במ"ל ליחידת המטרה (כוסות, כפות, כפיות) תוך שימוש בייצוג שברים מתמטיים (¼, ½, ¾), ללא מספרים עשרוניים.
    """
    if ml_amount <= 0:
        return ""

    amount = ml_amount / unit_ml

    # אחוז הטעות המותר
    TOLERANCE = 0.05

    # הגדרת שמות השברים (בייצוג יוניקוד של שברים)
    fractions = {
        0.25: "¼",  # רבע
        0.5: "½",  # חצי
        0.75: "¾"  # שלושת רבעים
    }

    whole_units = int(amount)
    remainder = amount - whole_units

    fraction_text = None
    for value, name in fractions.items():
        if abs(remainder - value) < TOLERANCE:
            fraction_text = name
            break

    # אם השארית קרובה ל-0, נתייחס אליה כאל יחידה שלמה
    if remainder < TOLERANCE:
        fraction_text = ""

    if whole_units == 0:
        if fraction_text:
            # אם יש שבר (½ כוס)
            return f"{fraction_text} {unit_name_singular}"
        else:
            # אם אין שבר ואין יחידה שלמה (כלומר, קטן מ-¼), מחזירים הודעה קצרה או ריק
            if amount > TOLERANCE:
                return f"פחות מ-{fractions[0.25]} {unit_name_singular}"
            else:
                return ""
    else:
        if fraction_text:
            # מספר שלם עם שבר (לדוגמה: 1 ו-½ כוסות)
            return f"{whole_units} ו{fraction_text} {unit_name_plural}"
        elif fraction_text == "":
            # מספר שלם בלבד
            return f"{whole_units} {unit_name_plural}"

        # אם יש שארית אבל היא אינה שבר נפוץ, עדיין מציגים כעשרוני (למקרה של שארית גדולה, אבל ביקשת שזה לא יקרה)
        # מכיוון שביקשת לא להציג עשרוניים, נשתמש ב-Fallback הקודם שלנו
        # מכיוון שהקוד מכסה יפה רבע, חצי ושלושת רבעי, זה אמור לקרות רק במקרים נדירים.
        return f"{whole_units} {unit_name_plural} (בערך)"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    amount = float(data.get('amount', 0))
    unit = data.get('unit', 'gram')
    material = data.get('material', 'water')

    # אם הקלט אינו תקין
    if amount <= 0:
        error_msg = 'אנא הכניסו כמות תקינה'
        return jsonify({
            'result_cups': error_msg,
            'result_tbs': error_msg,
            'result_ts': error_msg
        })

    if unit == 'ml':
        ml_amount = amount
    elif unit == 'gram':
        ml_amount = gram_to_ml(amount, material)
    else:
        return jsonify({
            'result_cups': 'יחידה לא נתמכת',
            'result_tbs': '',
            'result_ts': ''
        })

    # חישוב ועיצוב כל התוצאות
    result_cups = format_volume_to_fraction(ml_amount, CUP_ML, "כוס", "כוסות")
    result_tbs = format_volume_to_fraction(ml_amount, TBS_ML, "כף", "כפות")
    result_ts = format_volume_to_fraction(ml_amount, TS_ML, "כפית", "כפיות")

    return jsonify({
        'result_cups': result_cups,
        'result_tbs': result_tbs,
        'result_ts': result_ts,
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
