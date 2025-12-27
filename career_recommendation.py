from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Career Path Finder</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(to right, #83a4d4, #b6fbff); font-family: 'Segoe UI', sans-serif; }
        .container { margin-top: 50px; max-width: 800px; }
        .card { border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .btn-primary, .btn-success { width: 100%; }
        footer { margin-top: 30px; text-align: center; color: #fff; }
    </style>
</head>
<body>
<div class="container">
    <div class="card p-4">
        <h2 class="text-center text-primary">Career Recommendation System</h2>
        {% if not started %}
            <form method="POST">
                <div class="mb-3">
                    <label for="name" class="form-label">Your Name</label>
                    <input type="text" name="name" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label for="age" class="form-label">Your Age</label>
                    <input type="number" name="age" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary">Start</button>
            </form>
        {% elif study_roadmap %}
            <h4 class="text-warning">You are under 18, {{ name }}. Here's a study roadmap for you:</h4>
            <p>{{ roadmap }}</p>
            <a href="/" class="btn btn-secondary mt-3">Start Over</a>
        {% elif underage %}
            <form method="POST">
                <input type="hidden" name="name" value="{{ name }}">
                <input type="hidden" name="age" value="{{ age }}">
                <p>Please answer the following to get a study recommendation:</p>
                <div class="mb-3">
                    <label class="form-label">1. Which field interests you?</label>
                    <select class="form-select" name="field">
                        <option value="software">Software</option>
                        <option value="medical">Medical</option>
                        <option value="teaching">Teaching</option>
                        <option value="banking">Banking</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">2. How do you prefer to learn?</label>
                    <select class="form-select" name="learning">
                        <option value="online">Online courses</option>
                        <option value="books">Books & Guides</option>
                        <option value="hands_on">Hands-on projects</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-success">Get Study Roadmap</button>
            </form>
        {% elif not submitted %}
            <form method="POST">
                <input type="hidden" name="name" value="{{ name }}">
                <input type="hidden" name="age" value="{{ age }}">
                <p>Hello <strong>{{ name }}</strong>, please answer the following:</p>
                {% for i in range(1, 16) %}
                <div class="mb-3">
                    <label class="form-label">{{ questions[i-1]['q'] }}</label>
                    <select class="form-select" name="q{{ i }}">
                        {% for opt in questions[i-1]['options'] %}
                        <option value="{{ opt }}">{{ opt }}</option>
                        {% endfor %}
                    </select>
                </div>
                {% endfor %}
                <button type="submit" class="btn btn-success">Get Career Suggestions</button>
            </form>
        {% else %}
            <h4 class="text-success">Hello {{ name }}, based on your profile, we suggest:</h4>
            <ul>
                {% for career in recommendations %}
                    <li><strong>{{ career['title'] }}</strong> - Salary: ₹{{ career['salary'] }}/year<br><small>{{ career['req'] }}</small></li>
                {% endfor %}
            </ul>
            <a href="/" class="btn btn-secondary mt-3">Start Over</a>
        {% endif %}
    </div>
</div>
<footer>
    <p>Made with ❤ using Flask & Bootstrap</p>
</footer>
</body>
</html>
"""

questions = [
    {"q": "1. Highest education level?", "options": ["10th", "12th", "Diploma", "Graduation", "Post-Graduation"]},
    {"q": "2. Grade in last exam?", "options": ["Below 50%", "50-60%", "60-75%", "Above 75%"]},
    {"q": "3. Preferred education medium?", "options": ["English", "Local Language", "Both"]},
    {"q": "4. Are you open to relocate for studies or job?", "options": ["Yes", "No"]},
    {"q": "5. Are you currently enrolled in any educational program?", "options": ["Yes", "No"]},
    {"q": "6. Which field interests you the most?", "options": [
        "Software", "Medical", "Teaching", "Banking",
        "Technical", "Medical & Paramedical", "Creative & Design", "Government Jobs", "Defense", "Distance Education"]},
    {"q": "7. Which activity do you prefer?", "options": ["Team work", "Solo projects", "Customer interaction", "Creative work"]},
    {"q": "8. Years of experience in preferred field?", "options": ["0", "1-2", "3-5", "5+"]},
    {"q": "9. Expected monthly salary?", "options": ["< ₹20,000", "₹20,000-₹40,000", "₹40,000-₹70,000", "₹70,000+"]},
    {"q": "10. Do you prefer work from home?", "options": ["Yes", "No", "Flexible"]},
    {"q": "11. Comfort with technology?", "options": ["Low", "Moderate", "High"]},
    {"q": "12. Willingness to travel for work?", "options": ["Yes", "No"]},
    {"q": "13. How do you handle stress?", "options": ["Poorly", "Okay", "Well"]},
    {"q": "14. Do you enjoy problem-solving?", "options": ["Yes", "No"]},
    {"q": "15. Long-term career goal?", "options": ["Stability", "Growth", "Passion", "Money"]}
]
career_data = {
    "Software": [
        {"title": "Software Engineer", "salary": "600000", "req": "B.Tech or B.Sc in CS, strong coding skills"},
        {"title": "Web Developer", "salary": "500000", "req": "Knowledge of HTML, CSS, JavaScript, and a backend language"},
        {"title": "Mobile App Developer", "salary": "550000", "req": "Experience with Android or iOS development"},
        {"title": "Data Analyst", "salary": "600000", "req": "Excel, SQL, and knowledge of BI tools"},
        {"title": "UI/UX Designer", "salary": "450000", "req": "Design skills, Figma or Adobe XD"},
        {"title": "DevOps Engineer", "salary": "700000", "req": "CI/CD tools, cloud platforms"},
        {"title": "QA Tester", "salary": "400000", "req": "Manual or automated testing knowledge"},
        {"title": "Cybersecurity Analyst", "salary": "650000", "req": "Knowledge of security tools and protocols"}
    ],
    "Medical": [
        {"title": "Doctor (MBBS)", "salary": "800000", "req": "MBBS degree and medical license"},
        {"title": "Pharmacist", "salary": "450000", "req": "Diploma or Degree in Pharmacy"},
        {"title": "Nurse", "salary": "400000", "req": "Nursing Diploma or B.Sc Nursing"},
        {"title": "Radiologist Technician", "salary": "380000", "req": "Diploma in Radiology or X-Ray Tech"},
        {"title": "Physiotherapist", "salary": "500000", "req": "Bachelor's in Physiotherapy"},
        {"title": "Medical Lab Technician", "salary": "350000", "req": "Diploma in MLT"},
        {"title": "Paramedic", "salary": "320000", "req": "EMT Certification"},
        {"title": "Dental Assistant", "salary": "370000", "req": "Diploma in Dental Hygiene or Assistant"}
    ],
    "Teaching": [
        {"title": "Primary School Teacher", "salary": "300000", "req": "D.Ed or B.Ed"},
        {"title": "High School Teacher", "salary": "400000", "req": "Graduation + B.Ed"},
        {"title": "Special Education Teacher", "salary": "420000", "req": "Special Education Certification"},
        {"title": "Online Tutor", "salary": "360000", "req": "Subject knowledge, online teaching tools"},
        {"title": "College Lecturer", "salary": "500000", "req": "Post-Graduation + NET/PhD"},
        {"title": "Curriculum Designer", "salary": "550000", "req": "Education background and instructional design"},
        {"title": "Language Trainer", "salary": "380000", "req": "Language proficiency, teaching certificate"},
        {"title": "Corporate Trainer", "salary": "600000", "req": "Subject expertise, communication skills"}
    ],
    "Banking": [
        {"title": "Bank Clerk", "salary": "300000", "req": "10+2 or Graduation + Bank Exam"},
        {"title": "Bank PO", "salary": "500000", "req": "Graduation + IBPS/SBI PO"},
        {"title": "Loan Officer", "salary": "450000", "req": "Degree in Finance or Banking"},
        {"title": "Financial Analyst", "salary": "600000", "req": "B.Com/MBA Finance"},
        {"title": "Accounts Manager", "salary": "550000", "req": "Tally, Excel, B.Com"},
        {"title": "Investment Advisor", "salary": "620000", "req": "SEBI registered, finance knowledge"},
        {"title": "Customer Service Executive", "salary": "320000", "req": "Graduation + Soft Skills"},
        {"title": "Risk Manager", "salary": "700000", "req": "MBA Finance + Risk Training"}
    ],
    "Technical": [
        {"title": "Automobile Technician", "salary": "300000", "req": "Polytechnic in Automobile or ITI"},
        {"title": "Civil Engineering Assistant", "salary": "320000", "req": "Diploma in Civil Engineering"},
        {"title": "Electronic Mechanic", "salary": "340000", "req": "ITI or Diploma in Electronics"},
        {"title": "Tool and Die Maker", "salary": "360000", "req": "Specialized ITI or Vocational Training"},
        {"title": "Mechatronics Engineer", "salary": "400000", "req": "Diploma/BE in Mechatronics"},
        {"title": "Fire & Safety Technician", "salary": "300000", "req": "Diploma in Fire Engineering"},
        {"title": "HVAC Technician", "salary": "350000", "req": "ITI or Vocational Training"},
        {"title": "CNC Machine Operator", "salary": "330000", "req": "CNC Training Certification"}
    ],
    "Medical & Paramedical": [
        {"title": "Dark Room Assistant", "salary": "250000", "req": "Paramedical Certificate"},
        {"title": "Medical Lab Technician", "salary": "320000", "req": "Diploma in MLT"},
        {"title": "Nursing Assistant", "salary": "300000", "req": "Nursing Training Certificate"},
        {"title": "Pharma Sales Rep", "salary": "400000", "req": "Diploma in Pharmacy or Medical Rep Course"},
        {"title": "Dialysis Technician", "salary": "350000", "req": "Certificate or Diploma in Dialysis Tech"},
        {"title": "X-Ray Technician", "salary": "360000", "req": "Diploma in Radiography"},
        {"title": "Operation Theatre Assistant", "salary": "340000", "req": "Diploma in OT Technology"},
        {"title": "Optometrist Assistant", "salary": "330000", "req": "Diploma in Optometry"}
    ],
    "Creative & Design": [
        {"title": "3D Animator", "salary": "450000", "req": "Course in 3D Animation or VFX"},
        {"title": "Fashion Designer", "salary": "400000", "req": "Diploma in Apparel Design"},
        {"title": "Graphic Designer", "salary": "380000", "req": "Graphic Design Tools and Portfolio"},
        {"title": "Interior Designer", "salary": "450000", "req": "Course in Interior Design"},
        {"title": "Video Editor", "salary": "420000", "req": "Editing software like Premiere Pro, Final Cut"},
        {"title": "Game Designer", "salary": "500000", "req": "Game Design/Development Course"},
        {"title": "UI Designer", "salary": "460000", "req": "Figma, Sketch, Design Portfolio"},
        {"title": "Illustrator/Concept Artist", "salary": "400000", "req": "Strong sketching skills + portfolio"}
    ],
    "Government Jobs": [
        {"title": "Clerk (SSC, Railways)", "salary": "300000", "req": "10+2 + Competitive Exam"},
        {"title": "Police Constable", "salary": "320000", "req": "10th Pass + Physical Test + Written Exam"},
        {"title": "Railway Technician", "salary": "350000", "req": "ITI or Diploma + RRB Exam"},
        {"title": "Postman", "salary": "280000", "req": "10th Pass + India Post Exam"},
        {"title": "Forest Guard", "salary": "300000", "req": "12th Pass + Forest Department Exam"},
        {"title": "Income Tax Assistant", "salary": "400000", "req": "Graduation + SSC CGL"},
        {"title": "Excise Officer", "salary": "420000", "req": "Graduation + SSC/State PSC Exam"},
        {"title": "Stenographer", "salary": "350000", "req": "Typing skills + Stenography Certification"}
    ],
    "Defense": [
        {"title": "Soldier (Army)", "salary": "320000", "req": "10th Pass + Army Recruitment"},
        {"title": "Soldier GD (Air Force/Navy)", "salary": "340000", "req": "10th/12th + Entrance + Fitness"},
        {"title": "Nursing Assistant (Army)", "salary": "360000", "req": "12th + Biology + Military Training"},
        {"title": "Technical Entry (NDA)", "salary": "400000", "req": "12th with PCM + NDA Exam"},
        {"title": "Military Police", "salary": "330000", "req": "10th/12th + Defense Recruitment"},
        {"title": "Airman (Group Y)", "salary": "380000", "req": "12th + Air Force Selection"},
        {"title": "Naval Sailor", "salary": "370000", "req": "10+2 + Navy SSR/AA Exam"},
        {"title": "Tradesman Mate", "salary": "300000", "req": "10th Pass + Physical + Exam"}
    ],
    "Distance Education": [
        {"title": "Diploma in Computer Applications", "salary": "300000", "req": "6-month online course"},
        {"title": "Diploma in Business Management", "salary": "350000", "req": "1-year distance program"},
        {"title": "Certificate in Web Design", "salary": "320000", "req": "Online or distance certification"},
        {"title": "PG Diploma in HRM", "salary": "400000", "req": "Online MBA or HR course"},
        {"title": "BA via Open University", "salary": "280000", "req": "3-year distance degree"},
        {"title": "Diploma in Digital Marketing", "salary": "420000", "req": "Online certified course"},
        {"title": "Certificate in Data Entry", "salary": "270000", "req": "Basic typing and computer course"},
        {"title": "Remote IT Support Training", "salary": "350000", "req": "Online course in system/network support"}
    ]
}


study_roadmaps = {
    "software": "Start with basic programming (Python), then learn data structures, algorithms, and web development.",
    "medical": "Focus on biology and chemistry. Prepare for NEET after 12th.",
    "teaching": "Develop communication skills. Pursue B.Ed after graduation.",
    "banking": "Strengthen math and reasoning. Prepare for IBPS, SBI PO, etc."
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        try:
            age = int(age)
        except ValueError:
            return render_template_string(HTML_TEMPLATE, started=False)

        if age < 18:
            field = request.form.get("field")
            learning = request.form.get("learning")
            if field and learning:
                roadmap = study_roadmaps.get(field.lower(), "Explore various subjects and find your passion.")
                return render_template_string(HTML_TEMPLATE, started=True, study_roadmap=True, roadmap=roadmap, name=name)
            return render_template_string(HTML_TEMPLATE, started=True, underage=True, name=name, age=age)

        answers = [request.form.get(f"q{i}") for i in range(1, 16)]
        if all(answers):
            interest = answers[5]
            recommendation = career_data.get(interest, [])
            return render_template_string(HTML_TEMPLATE, started=True, underage=False, submitted=True, name=name, recommendations=recommendation)
        return render_template_string(HTML_TEMPLATE, started=True, underage=False, submitted=False, name=name, age=age, questions=questions)

    return render_template_string(HTML_TEMPLATE, started=False)

if __name__ == "__main__":
    app.run(debug=True)
