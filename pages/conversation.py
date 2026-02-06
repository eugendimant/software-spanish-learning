"""Conversation Mode with Goals page."""
import streamlit as st
import random
import re
from datetime import date

from utils.theme import render_hero, render_section_header
from utils.database import (
    save_conversation, record_progress, record_conversation_outcome,
    record_pragmatics_usage, get_conversation_outcome_stats
)
from utils.content import (
    CONVERSATION_SCENARIOS, NEGOTIATION_SCENARIOS, PRAGMATICS_PATTERNS
)
from utils.helpers import analyze_constraints, check_text_for_mistakes, detect_language


# ============== EXTENDED CONVERSATION SCENARIOS ==============

EXTENDED_SCENARIOS = [
    {
        "title": "Cita con el medico",
        "brief": "Necesitas explicar sintomas y entender el diagnostico.",
        "formality": "formal",
        "relationship": "professional",
        "relationship_label": "Authority Figure (Doctor)",
        "register_tips": "Use 'usted'. Be clear and organized. Ask for clarification if needed.",
        "hidden_targets": [
            "Describe sintomas con orden cronologico.",
            "Usa vocabulario medico basico (sintoma, diagnostico).",
            "Haz preguntas de clarificacion.",
        ],
        "opening": "Buenos dias, soy el doctor Martinez. Digame, que le trae por aqui hoy?",
        "system_role": "doctor",
        "response_templates": {
            "greeting": "Entiendo. Cuanto tiempo lleva con estos sintomas?",
            "symptoms": "Ya veo. Vamos a revisarle. Le duele si presiono aqui?",
            "question": "Buena pregunta. Le explico: {explanation}",
            "duration": "De acuerdo. Voy a recetarle algo para aliviar los sintomas.",
            "confirm": "Perfecto. Tome esto cada ocho horas durante una semana.",
            "closing": "Si no mejora en tres dias, vuelva a verme. Que se mejore.",
        },
    },
    {
        "title": "Devolver un producto",
        "brief": "El producto no funciona y quieres devolucion o cambio.",
        "formality": "formal",
        "relationship": "service_provider",
        "relationship_label": "Stranger (Store Employee)",
        "register_tips": "Use 'usted'. Be firm but polite. Have your receipt ready.",
        "hidden_targets": [
            "Explica el problema claramente.",
            "Usa condicionales de cortesia.",
            "Pide una solucion especifica.",
        ],
        "opening": "Buenas tardes, bienvenido a atencion al cliente. En que puedo ayudarle?",
        "system_role": "store_employee",
        "response_templates": {
            "greeting": "Entiendo. Tiene el ticket de compra?",
            "explain_problem": "Vaya, lo sentimos mucho. Cuando lo compro?",
            "have_receipt": "Perfecto. Dejeme verificar en el sistema... Si, aqui lo tengo.",
            "request_refund": "Puedo ofrecerle un cambio por otro igual o la devolucion del importe.",
            "request_exchange": "Claro, vamos a buscarle otro igual. Si prefiere otro modelo, le hacemos la diferencia.",
            "confirm": "Muy bien, procesamos la devolucion. Tardara 3-5 dias habiles.",
            "closing": "Aqui tiene su comprobante. Disculpe las molestias.",
        },
    },
    {
        "title": "Pedir indicaciones",
        "brief": "Estas perdido y necesitas llegar a un lugar especifico.",
        "formality": "neutral",
        "relationship": "stranger",
        "relationship_label": "Stranger (Passerby)",
        "register_tips": "Can use 'tu' or 'usted' depending on age. Be polite and grateful.",
        "hidden_targets": [
            "Usa formulas de cortesia para pedir ayuda.",
            "Confirma que has entendido las indicaciones.",
            "Agradece apropiadamente.",
        ],
        "opening": "Si, digame?",
        "system_role": "passerby",
        "response_templates": {
            "greeting": "Claro, conozco esa zona. Adonde quiere ir exactamente?",
            "ask_directions": "Vale, mire. Siga todo recto por esta calle unos 200 metros.",
            "continue": "Luego gire a la izquierda en el semaforo. Lo vera a mano derecha.",
            "confirm": "Eso es, justo despues del banco. No tiene perdida.",
            "thanks": "De nada, que le vaya bien!",
            "lost": "A ver, vamos a ver... Esta usted aqui. Tiene que ir hacia alla.",
        },
    },
    {
        "title": "Reservar mesa en restaurante",
        "brief": "Quieres reservar para una ocasion especial.",
        "formality": "formal",
        "relationship": "service_provider",
        "relationship_label": "Stranger (Restaurant Staff)",
        "register_tips": "Use 'usted'. Specify date, time, and number of people clearly.",
        "hidden_targets": [
            "Especifica fecha, hora y numero de personas.",
            "Menciona si hay alguna ocasion especial.",
            "Confirma los detalles de la reserva.",
        ],
        "opening": "Restaurante El Mirador, buenas tardes. En que puedo ayudarle?",
        "system_role": "restaurant",
        "response_templates": {
            "greeting": "Por supuesto. Para que dia quiere la reserva?",
            "date": "Muy bien. Y a que hora le vendria bien?",
            "time": "Dejeme comprobar... Si, tenemos disponibilidad. Para cuantas personas?",
            "people": "Perfecto. Prefiere interior o terraza?",
            "special": "Que bonito! Le prepararemos algo especial. A que nombre hago la reserva?",
            "confirm": "Listo. Reserva para {details}. Le esperamos.",
            "closing": "Gracias por su reserva. Hasta pronto!",
        },
    },
    {
        "title": "Hablar con el vecino sobre ruido",
        "brief": "El vecino hace ruido por las noches y quieres solucionarlo.",
        "formality": "neutral",
        "relationship": "acquaintance",
        "relationship_label": "Acquaintance (Neighbor)",
        "register_tips": "Start polite. Balance assertiveness with maintaining good relations.",
        "hidden_targets": [
            "Introduce el tema con tacto.",
            "Explica como te afecta sin acusar.",
            "Propón una solucion.",
        ],
        "opening": "Hola, que tal? Queria hablar de algo contigo...",
        "system_role": "neighbor",
        "response_templates": {
            "greeting": "Claro, dimme. Pasa algo?",
            "introduce_problem": "Ah, no me habia dado cuenta. Lo siento mucho.",
            "explain_impact": "Tienes razon. Es que a veces se nos va la hora sin darnos cuenta.",
            "suggest_solution": "Me parece bien. Intentare tener mas cuidado a partir de ahora.",
            "accept": "Si, tienes razon. A las diez paro la musica. Te parece?",
            "closing": "Gracias por decirmelo. Cualquier cosa, me avisas.",
            "defensive": "Bueno, es que tampoco es tan tarde...",
        },
    },
    {
        "title": "Entrevista de trabajo informal",
        "brief": "Primera entrevista telefonica para un puesto interesante.",
        "formality": "formal",
        "relationship": "authority",
        "relationship_label": "Authority Figure (HR Manager)",
        "register_tips": "Use 'usted' unless invited to use 'tu'. Be professional but show personality.",
        "hidden_targets": [
            "Presenta tu experiencia de forma concisa.",
            "Muestra interes haciendo preguntas.",
            "Usa vocabulario profesional.",
        ],
        "opening": "Buenos dias, le llamo de Recursos Humanos. Tengo su curriculum delante. Cuenteme un poco sobre usted.",
        "system_role": "hr_manager",
        "response_templates": {
            "greeting": "Muy bien. Que le atrajo de nuestra oferta de trabajo?",
            "experience": "Interesante. Y cual diria que es su mayor fortaleza?",
            "strength": "Bien. Y tiene alguna pregunta sobre el puesto?",
            "question": "Buena pregunta. {answer}",
            "salary": "El rango salarial esta entre X y Y, dependiendo de la experiencia.",
            "closing": "Perfecto. Le llamaremos la proxima semana para informarle. Gracias por su tiempo.",
            "availability": "Podria incorporarse el mes que viene?",
        },
    },
    {
        "title": "Queja en el banco",
        "brief": "Hay un cargo incorrecto en tu cuenta y necesitas solucionarlo.",
        "formality": "formal",
        "relationship": "service_provider",
        "relationship_label": "Stranger (Bank Employee)",
        "register_tips": "Use 'usted'. Be firm and document everything. Ask for reference numbers.",
        "hidden_targets": [
            "Explica el problema con datos concretos.",
            "Solicita correccion y comprobante.",
            "Pide numero de referencia.",
        ],
        "opening": "Buenos dias. Bienvenido a atencion al cliente. En que puedo ayudarle?",
        "system_role": "bank_employee",
        "response_templates": {
            "greeting": "Entiendo. Tiene su DNI y numero de cuenta a mano?",
            "explain_problem": "Dejeme revisar su cuenta... Efectivamente, veo un cargo de esa cantidad.",
            "provide_details": "Voy a abrir una incidencia. Tardara 48-72 horas en resolverse.",
            "request_refund": "Si el cargo es incorrecto, se le reembolsara automaticamente.",
            "ask_reference": "Su numero de referencia es el {reference}. Guardelo.",
            "confirm": "Perfecto. Le llamaremos cuando este resuelto.",
            "closing": "Necesita algo mas? Que tenga buen dia.",
        },
    },
    {
        "title": "Cancelar una suscripcion",
        "brief": "Quieres cancelar un servicio pero te ponen dificultades.",
        "formality": "formal",
        "relationship": "service_provider",
        "relationship_label": "Stranger (Customer Retention)",
        "register_tips": "Use 'usted'. Be polite but firm. Don't accept alternatives if you don't want them.",
        "hidden_targets": [
            "Se claro sobre tu intencion de cancelar.",
            "Rechaza ofertas de forma educada.",
            "Confirma que la cancelacion esta procesada.",
        ],
        "opening": "Buenas tardes, departamento de fidelizacion. En que puedo ayudarle?",
        "system_role": "retention_agent",
        "response_templates": {
            "greeting": "Entiendo. Puedo preguntarle el motivo de la cancelacion?",
            "explain_reason": "Comprendo. Y si le ofrecemos un descuento del 50% por tres meses?",
            "reject_offer": "Ya veo. Que le pareceria pausar la suscripcion en vez de cancelar?",
            "insist_cancel": "De acuerdo, respeto su decision. Procedo con la cancelacion.",
            "confirm": "Cancelacion procesada. Recibira confirmacion por email en 24 horas.",
            "closing": "Gracias por haber sido cliente. Hasta pronto.",
            "last_offer": "Una ultima cosa: tenemos una oferta especial que quiza le interese...",
        },
    },
]

# Combine with existing scenarios
ALL_CONVERSATION_SCENARIOS = CONVERSATION_SCENARIOS + EXTENDED_SCENARIOS


# ============== EXTENDED NEGOTIATION SCENARIOS ==============

EXTENDED_NEGOTIATION_SCENARIOS = [
    {
        "title": "Negociar precio de coche usado",
        "brief": "Quieres comprar un coche de segunda mano y negociar el precio.",
        "objectives": [
            {"type": "information", "target": "get_history", "description": "Preguntar por el historial del vehiculo"},
            {"type": "negotiation", "target": "lower_price", "description": "Conseguir un descuento"},
            {"type": "confirmation", "target": "confirm_warranty", "description": "Confirmar garantia o revision"},
            {"type": "closure", "target": "agree_terms", "description": "Acordar condiciones finales"},
        ],
        "partner_responses": [
            {"trigger": "greeting", "response": "Hola, buenos dias. Viene por el coche del anuncio, verdad?"},
            {"trigger": "interest", "response": "Si, esta en muy buen estado. Lo he tenido yo desde nuevo."},
            {"trigger": "history", "response": "Tiene todas las revisiones en el taller oficial. Ningun accidente."},
            {"trigger": "price", "response": "El precio es de 12.000 euros. Es justo para lo que ofrece."},
            {"trigger": "negotiate", "response": "Bueno, podria dejarlo en 11.500 si cerramos hoy."},
            {"trigger": "warranty", "response": "Puedo incluir tres meses de garantia de motor y cambio."},
            {"trigger": "accept", "response": "Perfecto. Entonces quedamos en 11.500 con garantia incluida."},
        ],
        "scoring_rubric": {
            "got_information": 20,
            "negotiated_price": 25,
            "confirmed_warranty": 20,
            "used_politeness": 15,
            "natural_closure": 20,
        },
    },
    {
        "title": "Pedir aumento de sueldo",
        "brief": "Llevas tiempo en la empresa y mereces un aumento. Negocia profesionalmente.",
        "objectives": [
            {"type": "justification", "target": "present_achievements", "description": "Presentar tus logros"},
            {"type": "request", "target": "request_raise", "description": "Pedir el aumento"},
            {"type": "negotiation", "target": "negotiate_terms", "description": "Negociar condiciones"},
            {"type": "confirmation", "target": "get_commitment", "description": "Obtener compromiso"},
        ],
        "partner_responses": [
            {"trigger": "greeting", "response": "Pasa, sientate. Querias hablar de algo, no?"},
            {"trigger": "achievements", "response": "Si, he visto que has hecho un buen trabajo este ano."},
            {"trigger": "request", "response": "Entiendo. Cuanto tenias en mente?"},
            {"trigger": "amount", "response": "Es bastante. Dejame revisarlo con direccion."},
            {"trigger": "negotiate", "response": "Podriamos plantear un 8% ahora y revisar en seis meses."},
            {"trigger": "accept", "response": "Me parece razonable. Preparo la documentacion."},
            {"trigger": "commit", "response": "Te confirmo por email esta semana. Gracias por hablarlo."},
        ],
        "scoring_rubric": {
            "presented_value": 25,
            "made_clear_request": 20,
            "negotiated_professionally": 25,
            "got_commitment": 15,
            "maintained_relationship": 15,
        },
    },
    {
        "title": "Resolver problema con vecinos",
        "brief": "Los vecinos hacen obras ruidosas sin avisar. Negocia una solucion.",
        "objectives": [
            {"type": "diplomatic", "target": "introduce_topic", "description": "Introducir el tema con tacto"},
            {"type": "explanation", "target": "explain_impact", "description": "Explicar como te afecta"},
            {"type": "solution", "target": "propose_solution", "description": "Proponer solucion razonable"},
            {"type": "agreement", "target": "reach_agreement", "description": "Llegar a un acuerdo"},
        ],
        "partner_responses": [
            {"trigger": "greeting", "response": "Hola, que tal. Pasaba algo?"},
            {"trigger": "topic", "response": "Ah, las obras. Si, es que estamos reformando el bano."},
            {"trigger": "impact", "response": "No sabia que molestaba tanto. Lo siento."},
            {"trigger": "solution", "response": "Si, podemos limitar a ciertas horas. Que te parece?"},
            {"trigger": "hours", "response": "De 10 a 14 y de 17 a 19. Nos viene bien."},
            {"trigger": "accept", "response": "Perfecto. Avisamos cuando vayamos a hacer ruido fuerte."},
            {"trigger": "thanks", "response": "Gracias a ti por hablarlo. Cualquier cosa, me dices."},
        ],
        "scoring_rubric": {
            "diplomatic_approach": 25,
            "clear_communication": 20,
            "reasonable_solution": 25,
            "maintained_relationship": 15,
            "got_agreement": 15,
        },
    },
    {
        "title": "Reclamar retraso de vuelo",
        "brief": "Tu vuelo se retraso 4 horas y quieres compensacion.",
        "objectives": [
            {"type": "documentation", "target": "document_issue", "description": "Documentar el problema"},
            {"type": "rights", "target": "cite_rights", "description": "Mencionar tus derechos"},
            {"type": "request", "target": "request_compensation", "description": "Pedir compensacion"},
            {"type": "confirmation", "target": "get_reference", "description": "Obtener numero de referencia"},
        ],
        "partner_responses": [
            {"trigger": "greeting", "response": "Buenas tardes. Atencion al pasajero. Digame."},
            {"trigger": "problem", "response": "Entiendo. Puede darme su numero de vuelo y fecha?"},
            {"trigger": "details", "response": "Si, veo el retraso registrado. Fue por causas operativas."},
            {"trigger": "rights", "response": "Efectivamente, tiene derecho a compensacion por el retraso."},
            {"trigger": "compensation", "response": "Le corresponden 400 euros segun la normativa europea."},
            {"trigger": "process", "response": "Puede solicitarlo online o le proceso la reclamacion ahora."},
            {"trigger": "reference", "response": "Su numero de reclamacion es CLM-2024-78432. Guardelo."},
        ],
        "scoring_rubric": {
            "documented_issue": 20,
            "knew_rights": 25,
            "got_compensation": 25,
            "got_reference": 15,
            "professional_tone": 15,
        },
    },
]

# Combine all negotiation scenarios
ALL_NEGOTIATION_SCENARIOS = NEGOTIATION_SCENARIOS + EXTENDED_NEGOTIATION_SCENARIOS


# ============== RESPONSE GENERATION SYSTEM ==============

def generate_partner_response(scenario: dict, user_message: str, turn: int, context: list) -> str:
    """
    Generate a contextual partner response based on scenario and user input.
    Uses template matching and keyword detection to provide relevant responses.
    """
    role = scenario.get("system_role", "generic")
    templates = scenario.get("response_templates", {})
    user_lower = user_message.lower()

    # Role-specific response generators
    response_generators = {
        "customer_service": generate_customer_service_response,
        "colleague": generate_colleague_response,
        "landlord": generate_landlord_response,
        "manager": generate_manager_response,
        "hotel_staff": generate_hotel_staff_response,
        "doctor": generate_doctor_response,
        "store_employee": generate_store_employee_response,
        "passerby": generate_passerby_response,
        "restaurant": generate_restaurant_response,
        "neighbor": generate_neighbor_response,
        "hr_manager": generate_hr_manager_response,
        "bank_employee": generate_bank_employee_response,
        "retention_agent": generate_retention_agent_response,
    }

    # Get the appropriate generator or use generic
    generator = response_generators.get(role, generate_generic_response)

    # Generate response
    response = generator(user_message, turn, context, templates)

    return response


def generate_customer_service_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for customer service scenarios."""
    user_lower = user_message.lower()

    # Check for key patterns
    if turn == 0:
        if any(word in user_lower for word in ["reembolso", "devolver", "dinero", "cobr"]):
            return "Entiendo su preocupacion. Podria indicarme el numero de su pedido o la fecha de la compra?"
        elif any(word in user_lower for word in ["problem", "fallo", "funciona", "roto"]):
            return "Lamento escuchar eso. Podria describirme exactamente que problema tiene?"
        else:
            return "Claro, cuenteme. Que puedo hacer por usted?"

    elif turn == 1:
        if any(word in user_lower for word in ["fecha", "dia", "ayer", "semana", "mes"]):
            return "Dejeme verificar en el sistema... Si, veo su registro. El problema que menciona esta cubierto por nuestra garantia."
        elif any(word in user_lower for word in ["numero", "pedido", "referencia"]):
            return "Perfecto, ya lo tengo localizado. Veo que efectivamente hubo un problema con su pedido."
        else:
            return "Entiendo. Para poder ayudarle mejor, necesito algunos datos mas. Tiene el ticket o comprobante?"

    elif turn == 2:
        if any(word in user_lower for word in ["si", "tengo", "aqui"]):
            return "Muy bien. Puedo ofrecerle dos opciones: un reembolso completo o un cambio por otro producto. Que prefiere?"
        elif any(word in user_lower for word in ["no", "perdi", "tirar"]):
            return "No se preocupe, podemos verificarlo con su DNI o tarjeta de credito. Me permite el numero?"
        else:
            return "De acuerdo. Podemos procesar una devolucion. El importe se reflejara en 5-7 dias habiles."

    elif turn == 3:
        if any(word in user_lower for word in ["reembolso", "dinero", "devolu"]):
            return "Perfecto, proceso el reembolso. Recibira un correo de confirmacion en las proximas horas."
        elif any(word in user_lower for word in ["cambio", "otro", "nuevo"]):
            return "Muy bien, gestionamos el cambio. Puede pasar a recogerlo manana o se lo enviamos a casa."
        else:
            return "De acuerdo. Hay algo mas en lo que pueda ayudarle?"

    else:
        return "Perfecto. Queda todo registrado. Gracias por su paciencia. Que tenga buen dia."


def generate_colleague_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for colleague/coworker scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        if any(word in user_lower for word in ["plazo", "tiempo", "retraso", "tarde"]):
            return "Ya, es que tuve unos imprevistos. Sabes que no suelo retrasarme."
        elif any(word in user_lower for word in ["problema", "preocupa", "hablar"]):
            return "Claro, dimme. Que pasa?"
        else:
            return "Si, lo se. Estoy un poco agobiado con todo."

    elif turn == 1:
        if any(word in user_lower for word in ["entiendo", "comprendo", "se que"]):
            return "Gracias por entenderlo. La verdad es que ha sido complicado."
        elif any(word in user_lower for word in ["pero", "necesito", "importante"]):
            return "Tienes razon. Que propones? Como lo solucionamos?"
        else:
            return "Mira, puedo intentar tenerlo listo para el viernes. Te parece?"

    elif turn == 2:
        if any(word in user_lower for word in ["seria posible", "podria", "tal vez"]):
            return "Me parece razonable. Dejame ver como reorganizo mi agenda."
        elif any(word in user_lower for word in ["ayuda", "apoyo", "echarte una mano"]):
            return "Te lo agradeceria mucho. Con algo de ayuda puedo adelantarlo."
        else:
            return "Vale, me comprometo a tenerlo listo. Te aviso en cuanto lo tenga."

    else:
        return "Perfecto, quedamos asi entonces. Gracias por hablarlo conmigo."


def generate_landlord_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for landlord/rental negotiation scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        if any(word in user_lower for word in ["alquiler", "piso", "apartamento", "vivienda"]):
            return "Si, sigue disponible. Busca para entrar ya o mas adelante?"
        else:
            return "Si, digame. Que necesita saber sobre el inmueble?"

    elif turn == 1:
        if any(word in user_lower for word in ["precio", "euros", "mensual", "cuesta"]):
            return "El precio es de 850 euros al mes, mas gastos de comunidad que son unos 50."
        elif any(word in user_lower for word in ["cuando", "fecha", "entrar", "disponible"]):
            return "Podria entrar a partir del dia 1 del mes que viene. Le interesa verlo?"
        else:
            return "Tiene dos habitaciones, salon, cocina equipada y un bano completo."

    elif turn == 2:
        if any(word in user_lower for word in ["negociar", "bajar", "descuento", "menos"]):
            return "Mire, el precio ya es ajustado para la zona. Aunque para un inquilino estable podria considerar algo."
        elif any(word in user_lower for word in ["fianza", "deposito", "garantia"]):
            return "La fianza son dos meses. Es lo habitual por la ley."
        else:
            return "Si quiere, podemos quedar para que lo vea. Le va bien manana por la tarde?"

    elif turn == 3:
        if any(word in user_lower for word in ["contrato", "duracion", "ano", "renovar"]):
            return "El contrato es por un ano, renovable. Si se queda mas tiempo, mantenemos las condiciones."
        elif any(word in user_lower for word in ["perfecto", "me interesa", "quedamos", "bien"]):
            return "Estupendo. Le espero manana a las 6 entonces. Traiga el DNI por si acaso."
        else:
            return "Podria dejarlo en 825 si firma por dos anos. Que le parece?"

    else:
        return "Muy bien, pues quedamos asi. Le mando la direccion exacta por mensaje. Hasta manana."


def generate_manager_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for manager/authority figure scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        if any(word in user_lower for word in ["plazo", "extension", "mas tiempo"]):
            return "Entiendo. Cual es la situacion exactamente?"
        else:
            return "Claro, cuentame. Que necesitas?"

    elif turn == 1:
        if any(word in user_lower for word in ["imprevisto", "problema", "dificultad"]):
            return "Ya veo. Cuanto tiempo adicional necesitarias?"
        elif any(word in user_lower for word in ["complejo", "mas de lo esperado"]):
            return "Comprendo. Que parte esta dando mas problemas?"
        else:
            return "De acuerdo. Pero necesito entender mejor la situacion."

    elif turn == 2:
        if any(word in user_lower for word in ["semana", "dias", "viernes"]):
            return "Hmm, es bastante. Hay algo que puedas entregar parcialmente antes?"
        elif any(word in user_lower for word in ["parte", "avance", "algo"]):
            return "Eso me parece razonable. Prefiero algo parcial a tiempo que todo tarde."
        else:
            return "Mira, puedo darte hasta el miercoles, pero necesito un avance el lunes."

    else:
        return "De acuerdo, quedamos asi. Mantenme informado del progreso."


def generate_hotel_staff_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for hotel staff scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        if any(word in user_lower for word in ["habitacion", "problema", "queja"]):
            return "Lamento escuchar eso. Podria indicarme su numero de habitacion y el problema?"
        else:
            return "Por supuesto, en que puedo ayudarle?"

    elif turn == 1:
        if any(word in user_lower for word in ["ruido", "vecinos", "no dormir"]):
            return "Lo sentimos mucho. Podemos ofrecerle un cambio de habitacion si lo desea."
        elif any(word in user_lower for word in ["limpieza", "sucio", "bano"]):
            return "Mis disculpas. Envio a alguien de limpieza inmediatamente."
        elif any(word in user_lower for word in ["aire", "calefaccion", "frio", "calor"]):
            return "Entiendo. Envio al tecnico ahora mismo para revisarlo."
        else:
            return "Comprendo su molestia. Vamos a solucionarlo de inmediato."

    elif turn == 2:
        if any(word in user_lower for word in ["compensacion", "descuento", "gratis"]):
            return "Por supuesto. Le aplicamos un 20% de descuento en su estancia como compensacion."
        elif any(word in user_lower for word in ["cambio", "otra habitacion"]):
            return "Tenemos una habitacion superior disponible. Se la ofrecemos sin coste adicional."
        else:
            return "Ademas de resolver el problema, queremos compensarle. Que le parece una cena cortesia de la casa?"

    else:
        return "Perfecto. Le pido disculpas de nuevo. Si necesita algo mas, estamos a su disposicion."


def generate_doctor_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for doctor scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        return "Entiendo. Cuanto tiempo lleva con estos sintomas?"

    elif turn == 1:
        if any(word in user_lower for word in ["dias", "semana", "ayer"]):
            return "Ya veo. Ha tomado algo para aliviar las molestias?"
        else:
            return "De acuerdo. Y ha notado si empeora en algun momento del dia?"

    elif turn == 2:
        if any(word in user_lower for word in ["si", "tome", "ibuprofeno", "paracetamol"]):
            return "Bien. Voy a examinarle. Le duele si hago esto?"
        elif any(word in user_lower for word in ["no", "nada"]):
            return "Entiendo. Vamos a hacer algunas pruebas para ver que pasa."
        else:
            return "De acuerdo. Por los sintomas que describe, creo que puede ser una infeccion leve."

    else:
        return "Le voy a recetar un tratamiento. Tome esto cada 8 horas durante 7 dias. Si no mejora, vuelva."


def generate_store_employee_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for store employee scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        return "Entiendo. Tiene el ticket de compra?"

    elif turn == 1:
        if any(word in user_lower for word in ["si", "aqui", "tengo"]):
            return "Perfecto. Dejeme verificar... Si, lo veo en el sistema. El producto tiene garantia."
        else:
            return "No se preocupe, puedo buscarlo con su DNI. Me lo permite?"

    elif turn == 2:
        if any(word in user_lower for word in ["devolucion", "dinero", "reembolso"]):
            return "Muy bien, proceso la devolucion. El importe se reflejara en 3-5 dias."
        elif any(word in user_lower for word in ["cambio", "otro"]):
            return "Claro, puede elegir otro modelo. Si hay diferencia de precio, se la ajustamos."
        else:
            return "Puedo ofrecerle cambio por otro igual o devolucion del importe. Que prefiere?"

    else:
        return "Aqui tiene su comprobante. Disculpe las molestias. Que tenga buen dia."


def generate_passerby_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for asking directions scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        if any(word in user_lower for word in ["donde", "como llego", "busco"]):
            return "A ver... Si, conozco esa zona. Mire, siga todo recto por esta calle."
        else:
            return "Claro, digame. A donde quiere ir?"

    elif turn == 1:
        if any(word in user_lower for word in ["recto", "adelante", "sigo"]):
            return "Eso es. Unos 200 metros. Luego vera un semaforo. Gire a la izquierda ahi."
        else:
            return "Despues del semaforo, es la segunda calle a la derecha. Lo vera enseguida."

    elif turn == 2:
        if any(word in user_lower for word in ["izquierda", "derecha", "semaforo"]):
            return "Exacto. Esta justo al lado del banco, no tiene perdida."
        elif any(word in user_lower for word in ["lejos", "minutos", "cuanto"]):
            return "Esta a unos 5 minutos andando. Si va rapido, menos."
        else:
            return "Si, por ahi mismo. Si se pierde, pregunte por la plaza Mayor, esta al lado."

    else:
        return "De nada, que le vaya bien!"


def generate_restaurant_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for restaurant reservation scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        if any(word in user_lower for word in ["reservar", "mesa", "reserva"]):
            return "Por supuesto. Para que dia seria la reserva?"
        else:
            return "Buenas tardes. Quiere hacer una reserva?"

    elif turn == 1:
        # Check for date mentions
        if any(word in user_lower for word in ["sabado", "viernes", "domingo", "manana", "hoy"]):
            return "Muy bien. Y a que hora le vendria bien?"
        else:
            return "Entendido. Para cuantas personas seria?"

    elif turn == 2:
        if any(word in user_lower for word in ["personas", "dos", "cuatro", "ocho"]):
            return "Perfecto. Prefiere interior o terraza?"
        elif any(word in user_lower for word in ["nueve", "ocho", "diez", "21", "20"]):
            return "Dejeme comprobar... Si, tenemos mesa disponible. Para cuantas personas?"
        else:
            return "Tenemos disponibilidad. A que nombre hago la reserva?"

    elif turn == 3:
        if any(word in user_lower for word in ["cumpleanos", "aniversario", "celebrar", "especial"]):
            return "Que bonito! Le prepararemos algo especial. A que nombre la reserva?"
        elif any(word in user_lower for word in ["interior", "terraza", "fuera", "dentro"]):
            return "Perfecto. A que nombre hago la reserva?"
        else:
            return "Muy bien. Tiene alguna preferencia de mesa o algun requerimiento especial?"

    else:
        return "Listo, reserva confirmada. Le esperamos. Hasta pronto!"


def generate_neighbor_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for neighbor scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        if any(word in user_lower for word in ["ruido", "musica", "sonido", "noche"]):
            return "Ah, no me habia dado cuenta. Lo siento mucho."
        else:
            return "Dimme, pasa algo?"

    elif turn == 1:
        if any(word in user_lower for word in ["dormir", "trabajo", "madruga", "descansar"]):
            return "Tienes razon, no lo habia pensado. Es que a veces se nos va la hora."
        elif any(word in user_lower for word in ["entiendo", "problema"]):
            return "Gracias por decirmelo de buena manera. Intentare tener mas cuidado."
        else:
            return "Ya, lo siento de verdad. Que propones?"

    elif turn == 2:
        if any(word in user_lower for word in ["diez", "once", "hora"]):
            return "Me parece razonable. A partir de las diez bajo el volumen."
        elif any(word in user_lower for word in ["avisa", "llama", "dime"]):
            return "Claro, si vuelve a pasar, me dices y bajo enseguida."
        else:
            return "De acuerdo. Intentare que no se repita."

    else:
        return "Gracias por hablarlo conmigo. Cualquier cosa, me dices."


def generate_hr_manager_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for HR/interview scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        return "Muy bien. Y que le atrajo de nuestra oferta de trabajo?"

    elif turn == 1:
        if any(word in user_lower for word in ["empresa", "proyecto", "sector"]):
            return "Me alegra oirlo. Cual diria que es su mayor fortaleza profesional?"
        else:
            return "Interesante. Tiene experiencia previa en este tipo de puesto?"

    elif turn == 2:
        if any(word in user_lower for word in ["equipo", "comunicacion", "organizacion"]):
            return "Esas son cualidades importantes para el puesto. Tiene alguna pregunta sobre la posicion?"
        else:
            return "Bien. Como se ve en cinco anos?"

    elif turn == 3:
        if "?" in user_message:
            return "Buena pregunta. El equipo es de unas 10 personas y el ambiente es bastante colaborativo."
        else:
            return "Interesante. Y cuando podria incorporarse si fuera seleccionado?"

    else:
        return "Perfecto. Le llamaremos la proxima semana para informarle. Gracias por su tiempo."


def generate_bank_employee_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for bank employee scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        if any(word in user_lower for word in ["cargo", "cobro", "error"]):
            return "Entiendo. Tiene su DNI y numero de cuenta a mano?"
        else:
            return "Claro, cuenteme. Cual es el problema?"

    elif turn == 1:
        if any(word in user_lower for word in ["si", "aqui", "numero"]):
            return "Dejeme revisar su cuenta... Efectivamente, veo un cargo de esa cantidad. Cuando se supone que se realizo?"
        else:
            return "Para poder revisar su cuenta, necesito verificar su identidad. Tiene el DNI?"

    elif turn == 2:
        if any(word in user_lower for word in ["no autorice", "no reconozco", "fraude"]):
            return "Voy a abrir una incidencia por cargo no reconocido. Se resuelve en 48-72 horas."
        else:
            return "Veo el cargo aqui. Puede que sea un cobro duplicado. Voy a verificarlo."

    else:
        return "Su numero de referencia es el 2024-8472. Guardelo por si necesita hacer seguimiento. Algo mas?"


def generate_retention_agent_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate response for subscription cancellation scenarios."""
    user_lower = user_message.lower()

    if turn == 0:
        return "Entiendo que quiere cancelar. Puedo preguntarle el motivo?"

    elif turn == 1:
        if any(word in user_lower for word in ["precio", "caro", "economico"]):
            return "Comprendo. Que le pareceria un descuento del 50% durante tres meses?"
        elif any(word in user_lower for word in ["no uso", "no necesito"]):
            return "Entiendo. Podriamos pausar su suscripcion en vez de cancelarla. Asi no pierde sus datos."
        else:
            return "Lamento escuchar eso. Hay algo que podamos mejorar?"

    elif turn == 2:
        if any(word in user_lower for word in ["no", "quiero cancelar", "seguro"]):
            return "Respeto su decision. Antes de proceder, le ofrezco un mes gratis para pensarlo. Le interesa?"
        else:
            return "De acuerdo. Voy a procesar la cancelacion entonces."

    else:
        return "Cancelacion procesada. Recibira confirmacion por email. Gracias por haber sido cliente."


def generate_generic_response(user_message: str, turn: int, context: list, templates: dict) -> str:
    """Generate a generic response when no specific role is defined."""
    responses_by_turn = {
        0: [
            "Entiendo. Dejeme pensar un momento sobre lo que me dice...",
            "Ya veo. Cuenteme mas, por favor.",
            "Comprendo. Y que le gustaria hacer al respecto?",
        ],
        1: [
            "Tiene razon en algunos puntos. Sin embargo, me gustaria aclarar algo...",
            "Interesante. Puedo ver su perspectiva.",
            "De acuerdo. Pero hay algo que debemos considerar.",
        ],
        2: [
            "Aprecio su perspectiva. Podriamos considerar otra opcion?",
            "Me parece razonable. Que propone exactamente?",
            "Entiendo lo que dice. Hay alguna alternativa?",
        ],
        3: [
            "Bueno, eso me parece aceptable. Quedamos asi?",
            "Creo que podemos llegar a un acuerdo.",
            "Muy bien, me parece bien.",
        ],
    }

    turn_responses = responses_by_turn.get(turn, responses_by_turn[3])
    return random.choice(turn_responses)


# ============== TARGET ACHIEVEMENT CHECKING ==============

def check_target_achievement(user_messages: list, targets: list) -> dict:
    """
    Check which hidden targets the user has achieved based on their messages.
    Returns a dict with target names and whether they were achieved.
    """
    results = {}
    all_text = " ".join(user_messages).lower()

    for target in targets:
        target_lower = target.lower()
        achieved = False

        # Check for mitigators/hedging
        if "mitigador" in target_lower or "quiza" in target_lower or "tal vez" in target_lower:
            mitigators = ["quiza", "tal vez", "me parece", "podria ser", "a lo mejor", "posiblemente"]
            count = sum(1 for m in mitigators if m in all_text)
            if "2" in target:
                achieved = count >= 2
            else:
                achieved = count >= 1

        # Check for concessions (aunque, si bien)
        elif "concesion" in target_lower or "aunque" in target_lower:
            concessions = ["aunque", "si bien", "a pesar de", "no obstante", "sin embargo"]
            achieved = any(c in all_text for c in concessions)

        # Check for avoiding calques
        elif "evita" in target_lower and "calco" in target_lower:
            calques = ["aplicar para", "estoy excitado", "no problema"]
            achieved = not any(c in all_text for c in calques)

        # Check for precise verbs
        elif "verbo preciso" in target_lower:
            precise_verbs = ["afrontar", "plantear", "desactivar", "sopesar", "mediar", "tramitar"]
            achieved = any(v in all_text for v in precise_verbs)

        # Check for indirect requests
        elif "peticion indirecta" in target_lower or "seria posible" in target_lower:
            indirect = ["seria posible", "podria", "le importaria", "te importaria", "me gustaria"]
            achieved = any(i in all_text for i in indirect)

        # Check for formal register (usted)
        elif "registro formal" in target_lower or "usted" in target_lower:
            formal_markers = ["usted", "le", "su merced", "por favor", "le agradeceria"]
            achieved = any(m in all_text for m in formal_markers)

        # Check for politeness phrases
        elif "cortesia" in target_lower or "frases de cortesia" in target_lower:
            politeness = ["por favor", "le agradeceria", "seria tan amable", "disculpe", "perdone"]
            count = sum(1 for p in politeness if p in all_text)
            if "2" in target:
                achieved = count >= 2
            else:
                achieved = count >= 1

        # Check for concrete data/comparisons
        elif "datos" in target_lower or "comparaciones" in target_lower or "concretas" in target_lower:
            # Check for numbers or comparison words
            has_numbers = bool(re.search(r'\d+', all_text))
            comparisons = ["mas que", "menos que", "comparado con", "a diferencia", "similar"]
            has_comparison = any(c in all_text for c in comparisons)
            achieved = has_numbers or has_comparison

        # Check for justification/reasons
        elif "justifica" in target_lower or "razones" in target_lower:
            justifications = ["porque", "debido a", "ya que", "puesto que", "dado que", "es que"]
            achieved = any(j in all_text for j in justifications)

        # Check for offering solutions
        elif "solucion" in target_lower or "propone" in target_lower:
            solutions = ["propongo", "podriamos", "sugiero", "que tal si", "una opcion seria"]
            achieved = any(s in all_text for s in solutions)

        # Check for conditionals
        elif "condicional" in target_lower:
            conditionals = ["seria", "podria", "deberia", "habria", "tendria", "gustaria"]
            achieved = any(c in all_text for c in conditionals)

        # Check for chronological ordering (for symptoms)
        elif "cronologico" in target_lower or "orden" in target_lower:
            time_markers = ["primero", "luego", "despues", "al principio", "finalmente", "desde hace"]
            achieved = any(t in all_text for t in time_markers)

        # Check for medical vocabulary
        elif "vocabulario medico" in target_lower or "sintoma" in target_lower:
            medical = ["sintoma", "diagnostico", "tratamiento", "receta", "consulta", "dolor"]
            achieved = any(m in all_text for m in medical)

        # Check for clarification questions
        elif "clarificacion" in target_lower or "pregunta" in target_lower:
            clarifications = ["que significa", "podria explicar", "a que se refiere", "como", "cuando"]
            # Also check for question marks
            has_questions = "?" in all_text
            achieved = any(c in all_text for c in clarifications) or has_questions

        # Check for appropriate thanks
        elif "agradece" in target_lower or "gracias" in target_lower:
            thanks = ["gracias", "se lo agradezco", "muy amable", "muchas gracias"]
            achieved = any(t in all_text for t in thanks)

        # Check for tactful introduction
        elif "tacto" in target_lower or "introduce" in target_lower:
            tactful = ["queria comentarte", "no se si", "a lo mejor", "si me permites"]
            achieved = any(t in all_text for t in tactful)

        # Check for avoiding accusations (using "yo" instead of "tu")
        elif "sin acusar" in target_lower or "afecta" in target_lower:
            # Check for "me" statements vs "tu" accusations
            accusatory = ["tu siempre", "tu nunca", "es tu culpa", "tienes que"]
            achieved = not any(a in all_text for a in accusatory)

        # Check for firm but polite tone
        elif "firme" in target_lower and "educado" in target_lower:
            firm = ["necesito", "es importante", "insisto"]
            polite = ["por favor", "le agradeceria", "disculpe"]
            achieved = any(f in all_text for f in firm) and any(p in all_text for p in polite)

        # Check for listing problems clearly
        elif "enumera" in target_lower or "problemas claramente" in target_lower:
            listing = ["primero", "segundo", "ademas", "tambien", "por otro lado"]
            achieved = any(l in all_text for l in listing)

        # Check for specific compensation request
        elif "compensacion especifica" in target_lower:
            specific = ["descuento", "reembolso", "devolucion", "gratis", "gratuito", "%"]
            achieved = any(s in all_text for s in specific)

        # Check for professional vocabulary
        elif "vocabulario profesional" in target_lower:
            professional = ["experiencia", "proyecto", "objetivo", "responsabilidad", "logro", "habilidad"]
            achieved = any(p in all_text for p in professional)

        # Check for showing interest with questions
        elif "interes" in target_lower and "preguntas" in target_lower:
            # Count questions asked
            question_count = all_text.count("?")
            achieved = question_count >= 1

        # Check for clear cancellation intent
        elif "cancelar" in target_lower and "claro" in target_lower:
            cancel_intent = ["quiero cancelar", "deseo cancelar", "cancele", "darse de baja"]
            achieved = any(c in all_text for c in cancel_intent)

        # Check for politely rejecting offers
        elif "rechaza" in target_lower and "educada" in target_lower:
            polite_rejections = ["no gracias", "lo agradezco pero", "no me interesa", "prefiero no"]
            achieved = any(r in all_text for r in polite_rejections)

        # Default: check if target keywords appear
        else:
            # Extract key words from target
            keywords = [w for w in target_lower.split() if len(w) > 4]
            achieved = any(kw in all_text for kw in keywords[:3])

        results[target] = achieved

    return results


def get_user_messages_text(messages: list) -> list:
    """Extract text from user messages only."""
    return [msg["content"] for msg in messages if msg.get("role") == "user"]


# ============== NEGOTIATION RESPONSE GENERATION ==============

def generate_negotiation_response(scenario: dict, user_message: str, step: int) -> str:
    """
    Generate a contextual response for negotiation scenarios.
    Analyzes user message and returns an appropriate partner response.
    """
    user_lower = user_message.lower()
    responses = scenario.get("partner_responses", [])

    # Keywords that trigger specific responses
    triggers = {
        "greeting": ["hola", "buenos dias", "buenas tardes", "vengo por"],
        "interest": ["interesa", "me gusta", "buen estado", "bonito"],
        "history": ["historial", "revisiones", "kilometros", "accidente", "dueno"],
        "price": ["precio", "cuesta", "euros", "cuanto", "vale"],
        "negotiate": ["podria", "descuento", "bajar", "menos", "negociar", "ajustar"],
        "warranty": ["garantia", "revision", "incluye", "seguro"],
        "accept": ["perfecto", "de acuerdo", "me parece bien", "acepto", "vale"],
        "topic": ["ruido", "obras", "molesta", "problema"],
        "impact": ["no puedo dormir", "trabajo", "afecta", "dificil"],
        "solution": ["propongo", "que tal si", "podriamos", "solucion"],
        "hours": ["hora", "manana", "tarde", "cuando"],
        "achievements": ["logros", "proyecto", "consegui", "hice", "mejore"],
        "request": ["aumento", "subida", "sueldo", "salario"],
        "amount": ["por ciento", "%", "euros", "cantidad"],
        "commit": ["cuando", "confirma", "seguro", "fecha"],
        "problem": ["retraso", "vuelo", "cancelado", "perdido"],
        "details": ["numero", "fecha", "vuelo", "referencia"],
        "rights": ["derecho", "normativa", "ley", "reglamento"],
        "compensation": ["compensacion", "devolucion", "reembolso", "indemnizacion"],
        "process": ["como", "proceso", "tramite", "solicitar"],
        "reference": ["numero", "referencia", "codigo", "guardar"],
        "thanks": ["gracias", "agradezco", "amable"],
    }

    # Find the best matching trigger
    best_match = None
    max_matches = 0

    for trigger, keywords in triggers.items():
        matches = sum(1 for kw in keywords if kw in user_lower)
        if matches > max_matches:
            max_matches = matches
            best_match = trigger

    # Find response with matching trigger
    if best_match and max_matches > 0:
        for response in responses:
            if response.get("trigger") == best_match:
                return response.get("response", "Entiendo, dejeme pensar...")

    # Fall back to step-based response
    if step < len(responses):
        return responses[step].get("response", "Entiendo, continuemos...")

    # Default responses for later turns
    default_later_responses = [
        "Entiendo su posicion. Dejeme considerarlo.",
        "Tiene razon en eso. Podemos ajustarlo.",
        "Me parece razonable. Algo mas que considerar?",
        "Muy bien, creo que estamos llegando a un acuerdo.",
        "Perfecto. Podemos cerrar asi.",
    ]

    return random.choice(default_later_responses)


def check_negotiation_objectives(user_message: str, objectives: list, met_objectives: list) -> list:
    """
    Check which negotiation objectives the user has achieved.
    Returns list of newly achieved objectives.
    """
    user_lower = user_message.lower()
    newly_achieved = []

    # Define keyword patterns for different objective types
    objective_keywords = {
        "get_history": ["historial", "revisiones", "kilometros", "accidente", "dueno", "anterior"],
        "lower_price": ["descuento", "bajar", "menos", "ajustar", "podria dejar", "negociar"],
        "confirm_warranty": ["garantia", "incluye", "cubre", "seguro"],
        "agree_terms": ["de acuerdo", "acepto", "perfecto", "quedamos", "trato hecho"],
        "present_achievements": ["logre", "consegui", "mejore", "proyecto", "resultado"],
        "request_raise": ["aumento", "subida", "mejorar", "sueldo", "salario"],
        "negotiate_terms": ["propongo", "que tal", "podriamos", "alternativa"],
        "get_commitment": ["cuando", "fecha", "confirmar", "compromiso"],
        "introduce_topic": ["queria hablar", "comentarte", "tema", "asunto"],
        "explain_impact": ["me afecta", "no puedo", "dificil", "problema"],
        "propose_solution": ["propongo", "solucion", "que tal si", "podriamos"],
        "reach_agreement": ["de acuerdo", "perfecto", "quedamos", "genial"],
        "document_issue": ["vuelo", "fecha", "numero", "retraso"],
        "cite_rights": ["derecho", "normativa", "ley", "reglamento"],
        "request_compensation": ["compensacion", "reembolso", "devolucion"],
        "get_reference": ["referencia", "numero", "codigo", "documento"],
        "confirm_alternative_time": ["hora", "cuando", "dia", "fecha"],
        "confirm_price": ["precio", "cuesta", "cuanto", "euros"],
        "ask_duration": ["cuanto tarda", "tiempo", "duracion", "minutos"],
        "natural_goodbye": ["gracias", "adios", "hasta", "luego"],
        "explain_problem": ["problema", "fallo", "no funciona", "roto"],
        "request_solution": ["quiero", "necesito", "devolucion", "cambio"],
        "confirm_process": ["como", "cuando", "proceso", "pasos"],
    }

    for obj in objectives:
        target = obj.get("target", "")
        if target in met_objectives:
            continue

        keywords = objective_keywords.get(target, [])
        if any(kw in user_lower for kw in keywords):
            newly_achieved.append(target)

    return newly_achieved


def render_conversation_page():
    """Render the Conversation Mode with Goals page."""
    render_hero(
        title="Conversation Mode",
        subtitle="Goal-driven roleplay: negotiate rent, handle refunds, resolve conflicts. Real fluency shows up in task-based exchanges.",
        pills=["Task-Based", "Hidden Targets", "Repair Skills", "Outcome Scoring"]
    )

    # Initialize session state
    if "conv_scenario" not in st.session_state:
        st.session_state.conv_scenario = None
    if "conv_messages" not in st.session_state:
        st.session_state.conv_messages = []
    if "conv_turn" not in st.session_state:
        st.session_state.conv_turn = 0
    if "conv_completed" not in st.session_state:
        st.session_state.conv_completed = False
    if "conv_targets_achieved" not in st.session_state:
        st.session_state.conv_targets_achieved = []
    if "conv_mode" not in st.session_state:
        st.session_state.conv_mode = "standard"
    if "conv_objectives_met" not in st.session_state:
        st.session_state.conv_objectives_met = []
    if "conv_pragmatics_used" not in st.session_state:
        st.session_state.conv_pragmatics_used = []

    # Mode selection tabs
    tab1, tab2, tab3 = st.tabs([
        "Standard Scenarios",
        "Advanced Negotiations",
        "Repair Skills Practice"
    ])

    with tab1:
        st.session_state.conv_mode = "standard"
        if st.session_state.conv_scenario is None or st.session_state.conv_mode != "standard":
            render_scenario_selection()
        else:
            render_conversation()

    with tab2:
        st.session_state.conv_mode = "negotiation"
        render_negotiation_mode()

    with tab3:
        st.session_state.conv_mode = "repair"
        render_repair_skills_practice()


def render_scenario_selection():
    """Render scenario selection interface."""
    render_section_header("Choose a Scenario")

    st.markdown("""
    <div class="card-muted">
        Select a real-world scenario to practice. Each scenario has hidden language targets
        you'll need to achieve during the conversation. Pay attention to the formality and
        relationship context - they affect which register to use.
    </div>
    """, unsafe_allow_html=True)

    # Category filter
    categories = {
        "All": ALL_CONVERSATION_SCENARIOS,
        "Service": [s for s in ALL_CONVERSATION_SCENARIOS if s.get("relationship") in ["service_provider"]],
        "Work": [s for s in ALL_CONVERSATION_SCENARIOS if s.get("relationship") in ["coworker", "authority"]],
        "Social": [s for s in ALL_CONVERSATION_SCENARIOS if s.get("relationship") in ["stranger", "acquaintance"]],
        "Professional": [s for s in ALL_CONVERSATION_SCENARIOS if s.get("relationship") == "professional"],
    }

    selected_category = st.selectbox(
        "Filter by category:",
        list(categories.keys()),
        key="scenario_category_filter"
    )

    scenarios_to_show = categories[selected_category]

    # Scenario cards
    cols = st.columns(2)

    for i, scenario in enumerate(scenarios_to_show):
        with cols[i % 2]:
            # Formality badge color
            formality = scenario.get("formality", "neutral")
            formality_color = {
                "formal": "primary",
                "neutral": "warning",
                "informal": "secondary"
            }.get(formality, "muted")

            formality_icon = {
                "formal": "👔",
                "neutral": "🤝",
                "informal": "😊"
            }.get(formality, "💬")

            relationship_label = scenario.get("relationship_label", "Unknown")

            st.markdown(f"""
            <div class="card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0;">{scenario['title']}</h4>
                    <span class="pill pill-{formality_color}">{formality_icon} {formality.title()}</span>
                </div>
                <p style="color: #8E8E93; margin-bottom: 0.75rem;">{scenario['brief']}</p>
                <div style="background: rgba(99, 102, 241, 0.1); padding: 0.5rem 0.75rem; border-radius: 8px; font-size: 0.85rem;">
                    <strong>Speaking with:</strong> {relationship_label}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Start: {scenario['title']}", key=f"start_{i}", use_container_width=True):
                st.session_state.conv_scenario = scenario
                st.session_state.conv_messages = [
                    {"role": "system", "content": scenario.get("opening", "Buenos dias...")}
                ]
                st.session_state.conv_turn = 0
                st.session_state.conv_completed = False
                st.session_state.conv_targets_achieved = []
                st.rerun()

    # Random scenario option
    st.divider()
    if st.button("Surprise Me", use_container_width=True):
        st.session_state.conv_scenario = random.choice(ALL_CONVERSATION_SCENARIOS)
        st.session_state.conv_messages = [
            {"role": "system", "content": st.session_state.conv_scenario.get("opening", "Buenos dias...")}
        ]
        st.session_state.conv_turn = 0
        st.session_state.conv_completed = False
        st.session_state.conv_targets_achieved = []
        st.rerun()


def render_conversation():
    """Render the active conversation interface."""
    scenario = st.session_state.conv_scenario

    # Header
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"### {scenario['title']}")
        st.markdown(f"*{scenario['brief']}*")

    with col2:
        if st.button("Change Scenario"):
            st.session_state.conv_scenario = None
            st.session_state.conv_messages = []
            st.session_state.conv_turn = 0
            st.session_state.conv_completed = False
            st.session_state.conv_targets_achieved = []
            st.rerun()

    # Formality context banner - always visible
    formality = scenario.get("formality", "neutral")
    relationship_label = scenario.get("relationship_label", "")
    register_tips = scenario.get("register_tips", "")

    formality_icon = {"formal": "F", "neutral": "N", "informal": "C"}.get(formality, "?")
    formality_bg = {"formal": "rgba(99, 102, 241, 0.15)", "neutral": "rgba(251, 191, 36, 0.15)", "informal": "rgba(34, 197, 94, 0.15)"}.get(formality, "rgba(100, 116, 139, 0.15)")

    st.markdown(f"""
    <div style="background: {formality_bg}; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; gap: 1rem;">
        <span style="font-size: 1.2rem; font-weight: bold; background: rgba(0,0,0,0.1); padding: 0.25rem 0.5rem; border-radius: 4px;">{formality_icon}</span>
        <div>
            <strong>{formality.title()} Register</strong> - {relationship_label}
            <br><span style="font-size: 0.85rem; opacity: 0.8;">{register_tips}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Progress indicator
    targets = scenario.get("hidden_targets", [])
    achieved_count = len(st.session_state.conv_targets_achieved)
    total_targets = len(targets)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Turn", f"{st.session_state.conv_turn + 1}/6")
    with col2:
        st.metric("Targets", f"{achieved_count}/{total_targets}")
    with col3:
        progress_pct = (achieved_count / total_targets * 100) if total_targets > 0 else 0
        st.metric("Progress", f"{progress_pct:.0f}%")

    st.divider()

    # Chat interface
    chat_container = st.container()

    with chat_container:
        # Display messages
        for msg in st.session_state.conv_messages:
            role = msg["role"]
            content = msg["content"]
            corrections = msg.get("corrections", [])

            if role == "system":
                # System/partner message
                st.markdown(f"""
                <div class="chat-message">
                    <div class="chat-avatar">P</div>
                    <div class="chat-bubble">{content}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # User message
                st.markdown(f"""
                <div class="chat-message user">
                    <div class="chat-avatar">U</div>
                    <div class="chat-bubble">{content}</div>
                </div>
                """, unsafe_allow_html=True)

                # Show inline corrections if any
                if corrections:
                    for corr in corrections:
                        st.caption(f"[TIP] *{corr}*")

    # Check if conversation should end
    if st.session_state.conv_turn >= 5 and not st.session_state.conv_completed:
        st.session_state.conv_completed = True

    # Input or completion
    if st.session_state.conv_completed:
        render_conversation_summary()
    else:
        render_conversation_input()


def render_conversation_input():
    """Render the conversation input area."""
    scenario = st.session_state.conv_scenario

    st.markdown("### Your Response")

    # Response input
    user_input = st.text_area(
        "Type your response:",
        height=100,
        placeholder="Escriba su respuesta...",
        key=f"conv_input_{st.session_state.conv_turn}"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Send", type="primary", use_container_width=True):
            if user_input.strip():
                process_user_message(user_input)
            else:
                st.warning("Please type a response.")

    with col2:
        if st.button("End Conversation", use_container_width=True):
            st.session_state.conv_completed = True
            st.rerun()

    # Hidden targets hint (revealed progressively)
    if st.session_state.conv_turn >= 2:
        with st.expander("Hint: Language Targets"):
            targets = scenario.get("hidden_targets", [])
            achieved = st.session_state.conv_targets_achieved

            for i, target in enumerate(targets):
                if target in achieved:
                    st.markdown(f"[DONE] ~~{target}~~")
                elif i <= st.session_state.conv_turn // 2:
                    st.markdown(f"[TODO] {target}")


def process_user_message(message: str):
    """Process user's conversation message."""
    scenario = st.session_state.conv_scenario

    # Check language first
    lang_info = detect_language(message)
    language_warning = None

    if lang_info["language"] == "english":
        language_warning = "[EN] Please write in Spanish to practice your conversation skills!"
    elif lang_info["language"] == "mixed" and lang_info.get("confidence", 0) > 0.3:
        language_warning = "[MIX] Mixed language detected. Try using only Spanish for better practice."

    # Check for mistakes with error handling
    corrections = []
    try:
        mistakes = check_text_for_mistakes(message)
        for mistake in mistakes[:2]:  # Show max 2 corrections
            if mistake.get("tag") != "language":  # Skip language warnings in corrections
                corrections.append(f"{mistake['original']} -> {mistake['correction']}")
    except Exception:
        mistakes = []  # Gracefully handle errors in mistake checking

    # Add language warning to corrections if present
    if language_warning:
        corrections.insert(0, language_warning)

    # Add user message
    st.session_state.conv_messages.append({
        "role": "user",
        "content": message,
        "corrections": corrections
    })

    # Check hidden targets using the new check_target_achievement function
    targets = scenario.get("hidden_targets", [])
    user_messages = get_user_messages_text(st.session_state.conv_messages)

    try:
        # Use our new comprehensive target checking
        target_results = check_target_achievement(user_messages, targets)

        # Update achieved targets
        for target, achieved in target_results.items():
            if achieved and target not in st.session_state.conv_targets_achieved:
                st.session_state.conv_targets_achieved.append(target)

        # Also try the original constraint analysis as backup
        constraint_results = analyze_constraints(message, targets)
        for target, result in constraint_results.items():
            if result.get("met") and target not in st.session_state.conv_targets_achieved:
                st.session_state.conv_targets_achieved.append(target)
    except Exception:
        pass  # Gracefully handle errors in constraint analysis

    # Generate contextual partner response using the new system
    system_response = generate_partner_response(
        scenario=scenario,
        user_message=message,
        turn=st.session_state.conv_turn,
        context=st.session_state.conv_messages
    )

    st.session_state.conv_messages.append({
        "role": "system",
        "content": system_response
    })

    st.session_state.conv_turn += 1
    record_progress({"writing_words": len(message.split())})

    st.rerun()




def render_conversation_summary():
    """Render the conversation summary and feedback."""
    scenario = st.session_state.conv_scenario

    st.divider()
    render_section_header("Conversation Complete")

    # Calculate achievements
    targets = scenario.get("hidden_targets", [])
    achieved = st.session_state.conv_targets_achieved
    achievement_rate = len(achieved) / len(targets) * 100 if targets else 100

    # Summary card
    st.markdown(f"""
    <div class="card" style="text-align: center;">
        <h3>Mission Report: {scenario['title']}</h3>
        <div class="metric-value" style="color: {'#10b981' if achievement_rate >= 70 else '#f59e0b'};">
            {achievement_rate:.0f}%
        </div>
        <div class="metric-label">Targets Achieved</div>
    </div>
    """, unsafe_allow_html=True)

    # Target breakdown
    st.markdown("### Target Analysis")

    for target in targets:
        is_achieved = target in achieved
        icon = "✅" if is_achieved else "❌"
        st.markdown(f"{icon} {target}")

    # What you did well
    st.markdown("### What You Did Well")
    positives = []

    if achievement_rate >= 50:
        positives.append("Good use of the conversation constraints")
    if st.session_state.conv_turn >= 4:
        positives.append("Maintained engagement throughout the conversation")

    all_messages = [m["content"] for m in st.session_state.conv_messages if m["role"] == "user"]
    total_words = sum(len(m.split()) for m in all_messages)

    if total_words >= 50:
        positives.append("Good output volume - you produced substantial content")

    for pos in positives:
        st.markdown(f"- {pos}")

    if not positives:
        st.markdown("- Keep practicing! Every conversation is an opportunity to improve.")

    # One thing to repeat tomorrow
    st.markdown("### Focus for Tomorrow")

    unachieved = [t for t in targets if t not in achieved]
    if unachieved:
        st.markdown(f"🎯 **Practice this:** {unachieved[0]}")
    else:
        st.markdown("🎯 **Challenge:** Try a more difficult scenario!")

    # Save conversation
    save_conversation({
        "title": scenario["title"],
        "hidden_targets": targets,
        "messages": st.session_state.conv_messages,
        "achieved_targets": achieved,
        "completed": 1,
    })
    record_progress({"missions_completed": 1})

    # Restart options
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Try Again", use_container_width=True):
            st.session_state.conv_messages = [
                {"role": "system", "content": scenario.get("opening", "Buenos dias...")}
            ]
            st.session_state.conv_turn = 0
            st.session_state.conv_completed = False
            st.session_state.conv_targets_achieved = []
            st.rerun()

    with col2:
        if st.button("New Scenario", use_container_width=True):
            st.session_state.conv_scenario = None
            st.session_state.conv_messages = []
            st.session_state.conv_turn = 0
            st.session_state.conv_completed = False
            st.session_state.conv_targets_achieved = []
            st.rerun()


def render_negotiation_mode():
    """Render advanced negotiation scenarios with outcome scoring."""
    render_section_header("Advanced Negotiations")

    st.markdown("""
    <div class="card-muted">
        Practice real-world negotiations with specific objectives. Each scenario has
        measurable outcomes and a scoring rubric based on your language use.
    </div>
    """, unsafe_allow_html=True)

    # Initialize negotiation state
    if "neg_scenario" not in st.session_state:
        st.session_state.neg_scenario = None
    if "neg_messages" not in st.session_state:
        st.session_state.neg_messages = []
    if "neg_current_step" not in st.session_state:
        st.session_state.neg_current_step = 0
    if "neg_score" not in st.session_state:
        st.session_state.neg_score = {}

    if st.session_state.neg_scenario is None:
        # Scenario selection
        for i, scenario in enumerate(ALL_NEGOTIATION_SCENARIOS):
            with st.expander(f"**{scenario['title']}**", expanded=i==0):
                st.markdown(f"*{scenario['brief']}*")

                st.markdown("**Objectives:**")
                for obj in scenario.get("objectives", []):
                    st.markdown(f"- {obj['description']}")

                st.markdown("**Scoring criteria:**")
                rubric = scenario.get("scoring_rubric", {})
                for criterion, points in rubric.items():
                    st.caption(f"- {criterion.replace('_', ' ').title()}: {points} pts")

                if st.button(f"Start: {scenario['title']}", key=f"neg_start_{i}"):
                    st.session_state.neg_scenario = scenario
                    st.session_state.neg_messages = []
                    st.session_state.neg_current_step = 0
                    st.session_state.neg_score = {k: 0 for k in rubric.keys()}

                    # Add opening from partner
                    opening_response = scenario.get("partner_responses", [{}])[0]
                    st.session_state.neg_messages.append({
                        "role": "partner",
                        "content": opening_response.get("response", "Buenos dias, en que puedo ayudarle?")
                    })
                    st.rerun()
    else:
        render_negotiation_conversation()


def render_negotiation_conversation():
    """Render active negotiation conversation."""
    scenario = st.session_state.neg_scenario

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {scenario['title']}")
    with col2:
        if st.button("Reset Negotiation"):
            st.session_state.neg_scenario = None
            st.session_state.neg_messages = []
            st.rerun()

    # Objectives sidebar
    st.markdown("**Your Objectives:**")
    objectives = scenario.get("objectives", [])
    met_objectives = st.session_state.conv_objectives_met

    for obj in objectives:
        is_met = obj["target"] in met_objectives
        icon = "[DONE]" if is_met else "[TODO]"
        st.markdown(f"{icon} {obj['description']}")

    st.divider()

    # Display conversation
    for msg in st.session_state.neg_messages:
        if msg["role"] == "partner":
            st.markdown(f"""
            <div class="chat-message">
                <div class="chat-avatar">P</div>
                <div class="chat-bubble">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message user">
                <div class="chat-avatar">U</div>
                <div class="chat-bubble">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            if msg.get("pragmatics"):
                st.caption(f"Pragmatics used: {', '.join(msg['pragmatics'])}")

    # Check if negotiation complete
    if len(st.session_state.neg_messages) >= 8:
        render_negotiation_summary()
        return

    # Input
    user_input = st.text_area(
        "Your response:",
        height=100,
        placeholder="Escriba su respuesta...",
        key=f"neg_input_{len(st.session_state.neg_messages)}"
    )

    # Pragmatics helper
    with st.expander("Pragmatics Helper"):
        st.markdown("**Useful phrases for this negotiation:**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Requests:**")
            for pattern in PRAGMATICS_PATTERNS.get("softeners", {}).get("requests", [])[:3]:
                st.caption(f"- {pattern['phrase']}")

        with col2:
            st.markdown("**Backchanneling:**")
            for pattern in PRAGMATICS_PATTERNS.get("backchanneling", {}).get("understanding", [])[:3]:
                st.caption(f"- {pattern['phrase']}")

    if st.button("Send", type="primary", use_container_width=True):
        if user_input.strip():
            # Analyze pragmatics used
            pragmatics_found = []
            text_lower = user_input.lower()

            # Check for softeners
            for softener in PRAGMATICS_PATTERNS.get("softeners", {}).get("hedging", []):
                if softener["phrase"].lower() in text_lower:
                    pragmatics_found.append(softener["phrase"])
                    record_pragmatics_usage("softeners", softener["phrase"], is_production=True)

            # Check for backchanneling
            for backchannel in PRAGMATICS_PATTERNS.get("backchanneling", {}).get("understanding", []):
                if backchannel["phrase"].lower() in text_lower:
                    pragmatics_found.append(backchannel["phrase"])
                    record_pragmatics_usage("backchanneling", backchannel["phrase"], is_production=True)

            # Add user message
            st.session_state.neg_messages.append({
                "role": "user",
                "content": user_input,
                "pragmatics": pragmatics_found
            })

            # Update score for used politeness
            if pragmatics_found:
                st.session_state.neg_score["used_politeness"] = min(
                    st.session_state.neg_score.get("used_politeness", 0) + 5,
                    scenario.get("scoring_rubric", {}).get("used_politeness", 20)
                )

            # Check objectives using the improved function
            newly_achieved = check_negotiation_objectives(
                user_input,
                objectives,
                st.session_state.conv_objectives_met
            )
            for target in newly_achieved:
                if target not in st.session_state.conv_objectives_met:
                    st.session_state.conv_objectives_met.append(target)

            # Generate contextual partner response
            partner_msg = generate_negotiation_response(
                scenario=scenario,
                user_message=user_input,
                step=st.session_state.neg_current_step
            )

            st.session_state.neg_messages.append({
                "role": "partner",
                "content": partner_msg
            })

            st.session_state.neg_current_step += 1
            record_progress({"writing_words": len(user_input.split())})
            st.rerun()


def render_negotiation_summary():
    """Render negotiation outcome summary."""
    scenario = st.session_state.neg_scenario

    st.divider()
    render_section_header("Negotiation Complete")

    # Calculate total score
    rubric = scenario.get("scoring_rubric", {})
    score = st.session_state.neg_score

    # Add points for confirmed details
    met_count = len(st.session_state.conv_objectives_met)
    score["confirmed_details"] = min(met_count * 10, rubric.get("confirmed_details", 25))

    total = sum(score.values())
    max_total = sum(rubric.values())
    percentage = (total / max_total * 100) if max_total > 0 else 0

    # Display score
    st.markdown(f"""
    <div class="card" style="text-align: center;">
        <h3>{scenario['title']}</h3>
        <div class="metric-value" style="color: {'#10b981' if percentage >= 70 else '#f59e0b'};">
            {total}/{max_total} points ({percentage:.0f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Score breakdown
    st.markdown("### Score Breakdown")
    for criterion, max_points in rubric.items():
        earned = score.get(criterion, 0)
        st.progress(earned / max_points if max_points > 0 else 0)
        st.caption(f"{criterion.replace('_', ' ').title()}: {earned}/{max_points}")

    # Record outcomes
    for obj in scenario.get("objectives", []):
        achieved = obj["target"] in st.session_state.conv_objectives_met
        record_conversation_outcome(0, obj["type"], achieved, obj["description"])

    record_progress({"missions_completed": 1})

    if st.button("New Negotiation", use_container_width=True):
        st.session_state.neg_scenario = None
        st.session_state.neg_messages = []
        st.session_state.conv_objectives_met = []
        st.session_state.neg_score = {}
        st.rerun()


def render_repair_skills_practice():
    """Render repair skills practice mode."""
    render_section_header("Repair Skills Practice")

    st.markdown("""
    Practice essential repair skills for real conversations: asking for clarification,
    self-correction, and confirming understanding. These skills are crucial for
    maintaining fluent conversations even when you don't catch everything.
    """)

    # Get repair skills patterns
    repair_skills = PRAGMATICS_PATTERNS.get("repair_skills", {})

    # Skill categories
    skill_type = st.selectbox(
        "Choose a skill to practice:",
        list(repair_skills.keys()),
        format_func=lambda x: x.replace("_", " ").title()
    )

    patterns = repair_skills.get(skill_type, [])

    if not patterns:
        st.warning("No patterns available for this skill.")
        return

    # Display patterns
    st.markdown(f"### {skill_type.replace('_', ' ').title()} Phrases")

    for i, pattern in enumerate(patterns):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{pattern['phrase']}**")
            if pattern.get("register"):
                st.caption(f"Register: {pattern['register']}")
            if pattern.get("use"):
                st.caption(f"Use: {pattern['use']}")

        with col2:
            if st.button("Practice", key=f"practice_{skill_type}_{i}"):
                record_pragmatics_usage("repair_skills", pattern["phrase"])
                st.success("Phrase practiced!")

    # Practice scenario
    st.divider()
    st.markdown("### Practice Scenario")

    # Extended scenarios for each skill type
    scenarios = {
        "asking_clarification": [
            {
                "prompt": "The speaker said something too quickly. Ask them to repeat or clarify.",
                "partner": "Entonces quedamos a las siete y media en la estacion de Atocha para coger el AVE de las ocho menos cuarto.",
                "context": "Planning to meet someone at a train station",
                "follow_up": "Claro, perdon. Quedamos a las 7:30 en Atocha. El tren sale a las 7:45.",
            },
            {
                "prompt": "You didn't understand a technical term. Ask for clarification.",
                "partner": "El problema es que hay un desfase en el flujo de caja y necesitamos refinanciar la operacion.",
                "context": "Business meeting about finances",
                "follow_up": "Refinanciar significa buscar nuevas fuentes de financiacion para cubrir los gastos.",
            },
            {
                "prompt": "The speaker used slang you don't know. Ask what it means.",
                "partner": "El proyecto mola mucho pero esta chungo terminarlo a tiempo.",
                "context": "Casual work conversation in Spain",
                "follow_up": "Ah, perdon. Mola significa que es bueno, y chungo que es dificil.",
            },
            {
                "prompt": "You couldn't hear well. Ask them to speak up.",
                "partner": "La reunion es en el edificio B, tercera planta, sala 302...",
                "context": "Getting directions in a noisy office",
                "follow_up": "Edificio B, tercera planta, sala 302. Tiene que subir por las escaleras de la derecha.",
            },
        ],
        "self_correction": [
            {
                "prompt": "You just made a mistake about the date. Correct yourself.",
                "partner": "Ya veo, entonces el proyecto empezara la proxima semana...",
                "context": "Discussing project timelines",
                "follow_up": "Ah, entiendo. Entonces empieza el lunes que viene, no este.",
            },
            {
                "prompt": "You used the wrong word. Correct yourself politely.",
                "partner": "Hmm, no estoy seguro de entender lo que quieres decir...",
                "context": "Explaining something at work",
                "follow_up": "Claro, ahora lo entiendo mejor. Gracias por aclararlo.",
            },
            {
                "prompt": "You gave the wrong information. Correct yourself.",
                "partner": "De acuerdo, entonces el presupuesto es de 5000 euros...",
                "context": "Budget discussion",
                "follow_up": "Entendido. 50.000 euros. Es una cifra importante.",
            },
            {
                "prompt": "You said the wrong name. Correct yourself.",
                "partner": "Espera, no conozco a ninguna Maria en ese departamento...",
                "context": "Discussing colleagues",
                "follow_up": "Ah si, Marta. Trabaja en el segundo piso, verdad?",
            },
        ],
        "confirming_understanding": [
            {
                "prompt": "Confirm that you understood the key points correctly.",
                "partner": "El contrato es por seis meses, con opcion de renovacion. El sueldo base es de 2500 euros mas bonus por objetivos.",
                "context": "Job offer discussion",
                "follow_up": "Exactamente. Y el bonus puede llegar hasta un 20% adicional.",
            },
            {
                "prompt": "Summarize what you understood about the process.",
                "partner": "Primero hay que rellenar el formulario online, luego esperar la aprobacion, y finalmente recoger el documento en persona.",
                "context": "Administrative process explanation",
                "follow_up": "Correcto. El proceso completo suele tardar unas dos semanas.",
            },
            {
                "prompt": "Confirm the meeting details.",
                "partner": "Nos vemos el jueves a las 4 en la cafeteria del centro comercial para revisar el proyecto.",
                "context": "Planning a work meeting",
                "follow_up": "Perfecto. Si hay algun cambio, te aviso.",
            },
            {
                "prompt": "Confirm you understood the instructions.",
                "partner": "Tienes que enviar el informe antes del viernes, con copia a tu supervisor y al cliente.",
                "context": "Receiving work instructions",
                "follow_up": "Eso es. Y recuerda incluir los graficos actualizados.",
            },
        ],
    }

    # Initialize scenario index if not exists
    scenario_index_key = f"repair_scenario_index_{skill_type}"
    if scenario_index_key not in st.session_state:
        st.session_state[scenario_index_key] = 0

    if skill_type in scenarios:
        scenario_list = scenarios[skill_type]
        current_index = st.session_state[scenario_index_key] % len(scenario_list)
        scene = scenario_list[current_index]

        # Show scenario number
        st.caption(f"Scenario {current_index + 1} of {len(scenario_list)}")

        # Context and situation
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.1); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <strong>Context:</strong> {scene['context']}
        </div>
        """, unsafe_allow_html=True)

        st.info(f"**Situation:** {scene['prompt']}")

        # Partner message in chat style
        st.markdown(f"""
        <div class="chat-message">
            <div class="chat-avatar">P</div>
            <div class="chat-bubble">{scene['partner']}</div>
        </div>
        """, unsafe_allow_html=True)

        response = st.text_area(
            "Your response (use the appropriate phrase):",
            height=100,
            placeholder="Escriba su respuesta usando una de las frases de arriba...",
            key=f"repair_response_{skill_type}_{current_index}"
        )

        # Track check state
        repair_checked_key = f"repair_checked_{skill_type}_{current_index}"
        repair_result_key = f"repair_result_{skill_type}_{current_index}"

        if repair_checked_key not in st.session_state:
            st.session_state[repair_checked_key] = False
            st.session_state[repair_result_key] = None

        col1, col2 = st.columns(2)

        with col1:
            if not st.session_state[repair_checked_key]:
                if st.button("Check Response", type="primary", use_container_width=True):
                    if response.strip():
                        # Check if any repair phrase was used
                        response_lower = response.lower()
                        used_pattern = None

                        for pattern in patterns:
                            # Check for various patterns
                            phrase = pattern["phrase"].lower()
                            phrase_start = phrase.split("...")[0].strip()
                            phrase_start_alt = phrase.split("?")[0].strip()

                            if phrase_start and len(phrase_start) > 3 and phrase_start in response_lower:
                                used_pattern = pattern["phrase"]
                                break
                            elif phrase_start_alt and len(phrase_start_alt) > 3 and phrase_start_alt in response_lower:
                                used_pattern = pattern["phrase"]
                                break
                            # Also check for key words
                            key_words = [w for w in phrase.split() if len(w) > 4]
                            if key_words and sum(1 for w in key_words if w in response_lower) >= 2:
                                used_pattern = pattern["phrase"]
                                break

                        if used_pattern:
                            st.session_state[repair_result_key] = {
                                "success": True,
                                "pattern": used_pattern,
                                "follow_up": scene.get("follow_up", "")
                            }
                            record_pragmatics_usage("repair_skills", used_pattern, is_production=True)
                            record_progress({"speaking_minutes": 0.5})
                        else:
                            st.session_state[repair_result_key] = {"success": False}

                        st.session_state[repair_checked_key] = True
                        st.rerun()
                    else:
                        st.warning("Please write a response.")

        with col2:
            if st.button("Skip to Next", use_container_width=True):
                st.session_state[scenario_index_key] = current_index + 1
                # Reset check state for new scenario
                st.session_state[repair_checked_key] = False
                st.session_state[repair_result_key] = None
                st.rerun()

        if st.session_state[repair_checked_key]:
            # Show result
            result = st.session_state[repair_result_key]

            if result and result["success"]:
                st.markdown(f"""
                <div style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <strong>[OK]</strong> Great! You used: '{result["pattern"]}'
                </div>
                """, unsafe_allow_html=True)

                # Show follow-up response from partner
                if result.get("follow_up"):
                    st.markdown("**Partner responds:**")
                    st.markdown(f"""
                    <div class="chat-message">
                        <div class="chat-avatar">P</div>
                        <div class="chat-bubble">{result["follow_up"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <strong>[TIP]</strong> Try incorporating one of the repair phrases from above.
                    <br><br>
                    <strong>Examples for this situation:</strong>
                    <ul>
                        <li>{patterns[0]["phrase"] if patterns else "No pattern available"}</li>
                        <li>{patterns[1]["phrase"] if len(patterns) > 1 else ""}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            if st.button("Try Next Scenario", type="primary", use_container_width=True):
                st.session_state[scenario_index_key] = current_index + 1
                st.session_state[repair_checked_key] = False
                st.session_state[repair_result_key] = None
                st.rerun()

    else:
        st.info("Select a skill type above to see practice scenarios.")
