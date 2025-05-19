from django.test import TestCase

# Create your tests here.


# {% extends 'base.html' %}

# {% block title %}Contact - Congenius{% endblock %}

# {% block content %}
#     <h1>Contact Form</h1>
#     <form method="POST" action="{% url 'contactUs' %}">
#         {% csrf_token %}
#         {{form}}
#         <button type="submit">Send</button>
#     </form>
# {% endblock %}


# {% extends 'base.html' %}

# {% block title %}Messages - Congenius{% endblock %}

# {% block content %}
#     <h1>Messages</h1>
#     {% if messages %}
#         <ul>
#             {% for message in messages %}
#                 <li>{{ message.nom }} -- {{ message.message }}</li>
#             {% endfor %}
#         </ul>
#     {% else %}
#         <p>Aucun message à afficher.</p>
#     {% endif %}
# {% endblock %}