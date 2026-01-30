"""Learning content data for VivaLingo Pro."""

# ============== TOPIC DIVERSITY DOMAINS ==============

TOPIC_DIVERSITY_DOMAINS = [
    {
        "domain": "Healthcare",
        "register": ["neutral", "formal"],
        "sample": "Tuve que pedir una segunda opinion para el diagnostico.",
        "keywords": ["salud", "diagnostico", "sintoma", "consulta", "tratamiento"],
        "lexicon": [
            {"term": "diagnostico", "meaning": "medical identification", "register": "formal", "pos": "noun",
             "contexts": [
                 "El medico confirmo el diagnostico despues de los analisis.",
                 "Mensaje: El diagnostico llego, todo bien.",
                 "Tras una semana de pruebas, el diagnostico revelo una infeccion menor."
             ]},
            {"term": "sintoma", "meaning": "clinical sign", "register": "neutral", "pos": "noun",
             "contexts": [
                 "El sintoma principal era fiebre alta.",
                 "Mensaje: Tengo los mismos sintomas de ayer.",
                 "Los sintomas desaparecieron tras el tratamiento."
             ]},
            {"term": "recetar", "meaning": "to prescribe treatment", "register": "formal", "pos": "verb",
             "contexts": [
                 "El medico me receto antibioticos.",
                 "Mensaje: Me han recetado reposo.",
                 "Decidio recetar un tratamiento alternativo."
             ]},
            {"term": "consulta", "meaning": "medical appointment", "register": "neutral", "pos": "noun",
             "contexts": [
                 "Tengo consulta manana a las 10.",
                 "Mensaje: Cancelo la consulta, no puedo ir.",
                 "La consulta duro mas de lo esperado."
             ]},
        ],
    },
    {
        "domain": "Housing",
        "register": ["formal", "neutral"],
        "sample": "El contrato de arrendamiento incluye clausulas de mantenimiento.",
        "keywords": ["alquiler", "contrato", "arrendamiento", "fianza", "piso"],
        "lexicon": [
            {"term": "arrendamiento", "meaning": "rental contract", "register": "formal", "pos": "noun",
             "contexts": [
                 "El arrendamiento es por un ano.",
                 "Mensaje: El arrendamiento vence en marzo.",
                 "Firmamos el arrendamiento con todas las clausulas."
             ]},
            {"term": "fianza", "meaning": "security deposit", "register": "neutral", "pos": "noun",
             "contexts": [
                 "La fianza equivale a dos meses de renta.",
                 "Mensaje: Pide que devuelvan la fianza.",
                 "Perdimos parte de la fianza por danos."
             ]},
            {"term": "clausula", "meaning": "contractual condition", "register": "formal", "pos": "noun",
             "contexts": [
                 "Esa clausula no me parece justa.",
                 "Mensaje: Revisa la clausula de penalizacion.",
                 "Anadimos una clausula sobre mascotas."
             ]},
            {"term": "inquilino", "meaning": "tenant", "register": "neutral", "pos": "noun",
             "contexts": [
                 "El inquilino anterior dejo el piso impecable.",
                 "Mensaje: El inquilino quiere renovar.",
                 "Como inquilino, tienes ciertos derechos."
             ]},
        ],
    },
    {
        "domain": "Relationships",
        "register": ["neutral", "casual"],
        "sample": "Necesitamos hablar con calma para aclarar lo que paso.",
        "keywords": ["relacion", "confianza", "pareja", "aclarar", "apoyo"],
        "lexicon": [
            {"term": "aclarar", "meaning": "to clarify / resolve misunderstanding", "register": "neutral", "pos": "verb",
             "contexts": [
                 "Quiero aclarar lo que dije ayer.",
                 "Mensaje: Necesito aclarar algo contigo.",
                 "Aclaramos el malentendido y seguimos adelante."
             ]},
            {"term": "apoyo", "meaning": "emotional support", "register": "neutral", "pos": "noun",
             "contexts": [
                 "Tu apoyo significa mucho para mi.",
                 "Mensaje: Gracias por el apoyo.",
                 "Sin su apoyo no habria podido lograrlo."
             ]},
            {"term": "confianza", "meaning": "trust in relationship", "register": "neutral", "pos": "noun",
             "contexts": [
                 "La confianza se construye con el tiempo.",
                 "Mensaje: Me cuesta recuperar la confianza.",
                 "Hay una base solida de confianza entre nosotros."
             ]},
            {"term": "distanciarse", "meaning": "to grow apart", "register": "neutral", "pos": "verb",
             "contexts": [
                 "Nos hemos distanciado ultimamente.",
                 "Mensaje: Siento que nos estamos distanciando.",
                 "Decidieron distanciarse por un tiempo."
             ]},
        ],
    },
    {
        "domain": "Travel problems",
        "register": ["neutral", "casual"],
        "sample": "El vuelo se retraso y perdimos la conexion.",
        "keywords": ["vuelo", "retraso", "conexion", "equipaje", "reserva"],
        "lexicon": [
            {"term": "retraso", "meaning": "delay in schedule", "register": "neutral", "pos": "noun",
             "contexts": [
                 "El retraso fue de tres horas.",
                 "Mensaje: Hay retraso, llegaremos tarde.",
                 "Nos compensaron por el retraso."
             ]},
            {"term": "reclamar", "meaning": "to file a claim / demand compensation", "register": "formal", "pos": "verb",
             "contexts": [
                 "Voy a reclamar el equipaje perdido.",
                 "Mensaje: Reclama la indemnizacion.",
                 "Reclamamos pero no nos hicieron caso."
             ]},
            {"term": "conexion", "meaning": "connecting flight/transport", "register": "neutral", "pos": "noun",
             "contexts": [
                 "Perdimos la conexion por el retraso.",
                 "Mensaje: Tenemos conexion en Madrid.",
                 "La conexion era demasiado ajustada."
             ]},
            {"term": "extraviar", "meaning": "to lose/misplace (luggage)", "register": "formal", "pos": "verb",
             "contexts": [
                 "Extraviaron mi maleta en el aeropuerto.",
                 "Mensaje: Han extraviado el equipaje.",
                 "Si extravian algo, tienes derecho a compensacion."
             ]},
        ],
    },
    {
        "domain": "Workplace conflict",
        "register": ["formal", "neutral"],
        "sample": "Tuvimos que mediar para evitar que el conflicto escalara.",
        "keywords": ["conflicto", "equipo", "reunion", "responsabilidad", "plazo"],
        "lexicon": [
            {"term": "mediar", "meaning": "to mediate / intervene to resolve", "register": "formal", "pos": "verb",
             "contexts": [
                 "Tuve que mediar entre los dos departamentos.",
                 "Mensaje: Alguien tiene que mediar.",
                 "Mediamos para encontrar una solucion."
             ]},
            {"term": "tension", "meaning": "state of friction/stress", "register": "neutral", "pos": "noun",
             "contexts": [
                 "Hay mucha tension en el equipo.",
                 "Mensaje: La tension es insostenible.",
                 "La tension disminuyo tras la reunion."
             ]},
            {"term": "responsabilidad", "meaning": "assigned obligation", "register": "formal", "pos": "noun",
             "contexts": [
                 "No quieren asumir la responsabilidad.",
                 "Mensaje: Es tu responsabilidad.",
                 "Repartimos las responsabilidades de forma equitativa."
             ]},
            {"term": "escalar", "meaning": "to escalate (a conflict)", "register": "neutral", "pos": "verb",
             "contexts": [
                 "El problema escalo rapidamente.",
                 "Mensaje: Esto puede escalar si no actuamos.",
                 "Evitamos que el conflicto escalara mas."
             ]},
        ],
    },
    {
        "domain": "Finance",
        "register": ["formal", "neutral"],
        "sample": "Necesito ajustar el presupuesto para cerrar el trimestre.",
        "keywords": ["presupuesto", "factura", "ingresos", "gastos", "ahorro"],
        "lexicon": [
            {"term": "presupuesto", "meaning": "budget / expense plan", "register": "formal", "pos": "noun",
             "contexts": [
                 "El presupuesto no cubre ese gasto.",
                 "Mensaje: Revisemos el presupuesto.",
                 "Aprobaron el presupuesto para el proyecto."
             ]},
            {"term": "liquidez", "meaning": "available cash / liquidity", "register": "formal", "pos": "noun",
             "contexts": [
                 "Tenemos problemas de liquidez.",
                 "Mensaje: Falta liquidez este mes.",
                 "La liquidez mejoro tras la venta."
             ]},
            {"term": "facturar", "meaning": "to invoice / bill", "register": "formal", "pos": "verb",
             "contexts": [
                 "Voy a facturar el servicio manana.",
                 "Mensaje: No olvides facturar.",
                 "Facturamos mas este trimestre."
             ]},
            {"term": "rentabilidad", "meaning": "profitability / return", "register": "formal", "pos": "noun",
             "contexts": [
                 "La rentabilidad del proyecto es alta.",
                 "Mensaje: Analiza la rentabilidad.",
                 "Buscamos mejorar la rentabilidad."
             ]},
        ],
    },
    {
        "domain": "Cooking",
        "register": ["neutral", "casual"],
        "sample": "Saltee las verduras antes de anadir la salsa.",
        "keywords": ["receta", "horno", "saltear", "sabor", "ingrediente"],
        "lexicon": [
            {"term": "saltear", "meaning": "to saute / quick-fry", "register": "neutral", "pos": "verb",
             "contexts": [
                 "Saltea las verduras a fuego alto.",
                 "Mensaje: Saltea la cebolla primero.",
                 "Salteamos los champiñones con ajo."
             ]},
            {"term": "ingrediente", "meaning": "recipe component", "register": "neutral", "pos": "noun",
             "contexts": [
                 "Nos falta un ingrediente clave.",
                 "Mensaje: Compra los ingredientes.",
                 "Cada ingrediente aporta un sabor unico."
             ]},
            {"term": "sazonar", "meaning": "to season / add spices", "register": "neutral", "pos": "verb",
             "contexts": [
                 "Sazona al gusto con sal y pimienta.",
                 "Mensaje: Sazona bien la carne.",
                 "Sazonamos con hierbas frescas."
             ]},
            {"term": "reposar", "meaning": "to rest (dough, meat)", "register": "neutral", "pos": "verb",
             "contexts": [
                 "Deja reposar la masa una hora.",
                 "Mensaje: Que repose antes de servir.",
                 "La carne debe reposar cinco minutos."
             ]},
        ],
    },
    {
        "domain": "Emotions",
        "register": ["neutral", "formal"],
        "sample": "Me invadio una mezcla de alivio y cansancio.",
        "keywords": ["emociones", "alivio", "ansiedad", "frustracion", "calma"],
        "lexicon": [
            {"term": "alivio", "meaning": "sense of relief", "register": "neutral", "pos": "noun",
             "contexts": [
                 "Senti un gran alivio al saberlo.",
                 "Mensaje: Que alivio, todo salio bien.",
                 "El alivio fue inmediato tras la noticia."
             ]},
            {"term": "frustracion", "meaning": "frustration from unmet expectations", "register": "formal", "pos": "noun",
             "contexts": [
                 "La frustracion me invadio.",
                 "Mensaje: Entiendo tu frustracion.",
                 "Canalizo la frustracion en algo productivo."
             ]},
            {"term": "serenar", "meaning": "to calm / soothe", "register": "formal", "pos": "verb",
             "contexts": [
                 "Intento serenarme antes de responder.",
                 "Mensaje: Serena el ambiente.",
                 "Logre serenar mis pensamientos."
             ]},
            {"term": "agobiar", "meaning": "to overwhelm / stress out", "register": "neutral", "pos": "verb",
             "contexts": [
                 "No quiero agobiarte con esto.",
                 "Mensaje: Me agobia la situacion.",
                 "Se siente agobiado por las responsabilidades."
             ]},
        ],
    },
    {
        "domain": "Bureaucracy",
        "register": ["formal"],
        "sample": "Hay que tramitar el documento antes del plazo.",
        "keywords": ["tramite", "documento", "solicitud", "plazo", "oficina"],
        "lexicon": [
            {"term": "tramitar", "meaning": "to process / handle paperwork", "register": "formal", "pos": "verb",
             "contexts": [
                 "Voy a tramitar el permiso manana.",
                 "Mensaje: Tramita la solicitud cuanto antes.",
                 "Tramitamos todo en una semana."
             ]},
            {"term": "solicitud", "meaning": "formal request / application", "register": "formal", "pos": "noun",
             "contexts": [
                 "La solicitud fue aprobada.",
                 "Mensaje: Envia la solicitud hoy.",
                 "Rechazaron la solicitud por falta de documentos."
             ]},
            {"term": "plazo", "meaning": "deadline / time limit", "register": "formal", "pos": "noun",
             "contexts": [
                 "El plazo vence el viernes.",
                 "Mensaje: Ojo con el plazo.",
                 "Ampliaron el plazo una semana mas."
             ]},
            {"term": "subsanar", "meaning": "to rectify / fix (an error in documents)", "register": "formal", "pos": "verb",
             "contexts": [
                 "Hay que subsanar los errores del formulario.",
                 "Mensaje: Subsana el error antes del plazo.",
                 "Subsanamos las deficiencias y reenviamos."
             ]},
        ],
    },
    {
        "domain": "Everyday slang-light",
        "register": ["casual"],
        "sample": "Que bajon, se cayo el plan a ultima hora.",
        "keywords": ["plan", "bajon", "rollo", "vale", "guay"],
        "lexicon": [
            {"term": "bajon", "meaning": "sudden disappointment / letdown", "register": "casual", "pos": "noun",
             "contexts": [
                 "Que bajon que no puedas venir.",
                 "Mensaje: Menudo bajon lo de ayer.",
                 "El bajon fue tremendo al enterarme."
             ]},
            {"term": "rollo", "meaning": "thing / situation / vibe (slang)", "register": "casual", "pos": "noun",
             "contexts": [
                 "No me va ese rollo.",
                 "Mensaje: Es buen rollo, tranquilo.",
                 "El rollo de siempre, ya sabes."
             ]},
            {"term": "guay", "meaning": "cool / great", "register": "casual", "pos": "adjective",
             "contexts": [
                 "Eso suena muy guay.",
                 "Mensaje: Guay, quedamos entonces.",
                 "La fiesta estuvo guay."
             ]},
            {"term": "molar", "meaning": "to be cool / to like", "register": "casual", "pos": "verb",
             "contexts": [
                 "Me mola mucho tu idea.",
                 "Mensaje: Mola el plan.",
                 "No me mola nada ese sitio."
             ]},
        ],
    },
]

# ============== VERB CHOICE STUDIO ==============

VERB_CHOICE_STUDIO = [
    {
        "scenario": "Quieres explicar que lograste sacar un proyecto adelante pese a obstaculos.",
        "options": [
            {"verb": "sacar adelante", "register": "neutral", "intensity": "alta",
             "implication": "superar obstaculos y completar algo complejo", "objects": "proyecto, iniciativa, proceso"},
            {"verb": "terminar", "register": "neutral", "intensity": "media",
             "implication": "completar sin enfatizar esfuerzo", "objects": "tarea, informe"},
            {"verb": "hacer", "register": "casual", "intensity": "baja",
             "implication": "accion generica, poco precisa", "objects": "cosas, trabajo"},
        ],
        "best": "sacar adelante",
        "also": ["terminar"],
        "contrast": ["Terminar suena neutro y no comunica la presion.", "Hacer es demasiado vago para este contexto."],
    },
    {
        "scenario": "Necesitas expresar que alcanzaste un objetivo medible.",
        "options": [
            {"verb": "alcanzar", "register": "formal", "intensity": "media",
             "implication": "logro cuantificable", "objects": "meta, objetivo, cifra"},
            {"verb": "conseguir", "register": "neutral", "intensity": "media",
             "implication": "logro general, menos tecnico", "objects": "resultado, permiso"},
            {"verb": "lograr", "register": "formal", "intensity": "alta",
             "implication": "esfuerzo destacado", "objects": "acuerdo, avance"},
        ],
        "best": "alcanzar",
        "also": ["lograr"],
        "contrast": ["Lograr es mas enfatico; usalo si quieres destacar esfuerzo.",
                     "Conseguir es correcto pero menos preciso para metas numericas."],
    },
    {
        "scenario": "Necesitas decir que evaluaste opciones con calma antes de decidir.",
        "options": [
            {"verb": "sopesar", "register": "formal", "intensity": "alta",
             "implication": "evaluacion cuidadosa y estrategica", "objects": "opciones, riesgos, propuestas"},
            {"verb": "considerar", "register": "neutral", "intensity": "media",
             "implication": "evaluacion neutra, menos intensa", "objects": "alternativas, posibilidades"},
            {"verb": "mirar", "register": "casual", "intensity": "baja",
             "implication": "revision general, poco profunda", "objects": "datos, opciones"},
        ],
        "best": "sopesar",
        "also": ["considerar"],
        "contrast": ["Sopesar implica deliberacion mas intensa que considerar.",
                     "Mirar es demasiado informal para contextos profesionales."],
    },
    {
        "scenario": "Quieres expresar que bajaste la tension en una reunion.",
        "options": [
            {"verb": "desactivar", "register": "neutral", "intensity": "alta",
             "implication": "neutralizar tension o conflicto de forma tactica", "objects": "tension, conflicto, discusion"},
            {"verb": "calmar", "register": "neutral", "intensity": "media",
             "implication": "reducir intensidad emocional", "objects": "ambiente, equipo"},
            {"verb": "parar", "register": "casual", "intensity": "alta",
             "implication": "detener de forma brusca", "objects": "conversacion, discusion"},
        ],
        "best": "desactivar",
        "also": ["calmar"],
        "contrast": ["Desactivar es mas tactico que calmar.",
                     "Parar suena brusco y puede generar mas tension."],
    },
    {
        "scenario": "Necesitas afirmar que insististe en cumplir una norma.",
        "options": [
            {"verb": "exigir", "register": "formal", "intensity": "alta",
             "implication": "imponer con autoridad o firmeza", "objects": "cumplimiento, respuesta, accion"},
            {"verb": "pedir", "register": "neutral", "intensity": "media",
             "implication": "solicitud neutra", "objects": "actualizacion, informacion"},
            {"verb": "sugerir", "register": "formal", "intensity": "baja",
             "implication": "propuesta suave sin presion", "objects": "mejoras, cambios"},
        ],
        "best": "exigir",
        "also": [],
        "contrast": ["Exigir es mas fuerte y formal que pedir.",
                     "Sugerir no comunica la firmeza necesaria."],
    },
    {
        "scenario": "Quieres decir que propusiste una idea para discutir.",
        "options": [
            {"verb": "plantear", "register": "formal", "intensity": "media",
             "implication": "introducir un tema para consideracion", "objects": "idea, problema, cuestion"},
            {"verb": "decir", "register": "casual", "intensity": "baja",
             "implication": "comunicar sin enfasis", "objects": "cualquier cosa"},
            {"verb": "presentar", "register": "formal", "intensity": "media",
             "implication": "mostrar de forma estructurada", "objects": "propuesta, informe"},
        ],
        "best": "plantear",
        "also": ["presentar"],
        "contrast": ["Plantear implica abrir el tema a debate.",
                     "Decir es demasiado generico para contextos profesionales."],
    },
    {
        "scenario": "Necesitas expresar que enfrentaste un problema dificil.",
        "options": [
            {"verb": "afrontar", "register": "formal", "intensity": "alta",
             "implication": "enfrentar con determinacion", "objects": "problema, reto, situacion"},
            {"verb": "lidiar con", "register": "neutral", "intensity": "media",
             "implication": "manejar algo complicado", "objects": "problemas, situaciones"},
            {"verb": "tratar", "register": "neutral", "intensity": "baja",
             "implication": "ocuparse de forma general", "objects": "temas, asuntos"},
        ],
        "best": "afrontar",
        "also": ["lidiar con"],
        "contrast": ["Afrontar comunica valentia y decision.",
                     "Tratar es demasiado neutro para problemas serios."],
    },
    {
        "scenario": "Quieres decir que gestionaste un proceso administrativo.",
        "options": [
            {"verb": "tramitar", "register": "formal", "intensity": "media",
             "implication": "gestionar papeles o procesos oficiales", "objects": "solicitud, permiso, documento"},
            {"verb": "hacer", "register": "casual", "intensity": "baja",
             "implication": "accion generica", "objects": "cualquier cosa"},
            {"verb": "gestionar", "register": "formal", "intensity": "media",
             "implication": "administrar de forma amplia", "objects": "proyecto, equipo, recursos"},
        ],
        "best": "tramitar",
        "also": ["gestionar"],
        "contrast": ["Tramitar es especifico para procesos burocraticos.",
                     "Hacer es impreciso para contextos formales."],
    },
    {
        "scenario": "Necesitas expresar que contribuiste algo valioso al equipo.",
        "options": [
            {"verb": "aportar", "register": "formal", "intensity": "media",
             "implication": "contribuir algo de valor", "objects": "ideas, recursos, experiencia"},
            {"verb": "dar", "register": "neutral", "intensity": "baja",
             "implication": "entregar sin enfasis", "objects": "cualquier cosa"},
            {"verb": "ofrecer", "register": "neutral", "intensity": "media",
             "implication": "poner a disposicion", "objects": "ayuda, servicios"},
        ],
        "best": "aportar",
        "also": ["ofrecer"],
        "contrast": ["Aportar enfatiza el valor de la contribucion.",
                     "Dar es demasiado neutro para destacar contribuciones."],
    },
    {
        "scenario": "Quieres decir que llevaste a cabo un plan complejo.",
        "options": [
            {"verb": "llevar a cabo", "register": "formal", "intensity": "alta",
             "implication": "ejecutar algo completo y complejo", "objects": "plan, proyecto, estrategia"},
            {"verb": "realizar", "register": "formal", "intensity": "media",
             "implication": "hacer de forma completa", "objects": "tarea, actividad"},
            {"verb": "hacer", "register": "casual", "intensity": "baja",
             "implication": "accion generica", "objects": "cualquier cosa"},
        ],
        "best": "llevar a cabo",
        "also": ["realizar"],
        "contrast": ["Llevar a cabo implica complejidad y completitud.",
                     "Hacer no transmite la escala del logro."],
    },
]

# ============== GRAMMAR PATTERNS ==============

GRAMMAR_MICRODRILLS = [
    {
        "focus": "Gender agreement",
        "prompt": "Selecciona la opcion correcta: La reunion fue ___ y productiva.",
        "options": ["intenso", "intensa", "intensas"],
        "answer": "intensa",
        "explanation": "Reunion es femenino singular, por eso requiere intensa.",
        "examples": ["La discusion fue intensa.", "La agenda estuvo cargada."],
        "category": "agreement",
    },
    {
        "focus": "Verb tense",
        "prompt": "Completa: Si ___ mas tiempo, habria terminado el informe.",
        "options": ["tengo", "tenia", "tuviera"],
        "answer": "tuviera",
        "explanation": "Condicional con si requiere imperfecto de subjuntivo.",
        "examples": ["Si tuviera apoyo, lo haria.", "Si fuera posible, lo ajustamos."],
        "category": "tense",
    },
    {
        "focus": "Ser vs estar",
        "prompt": "El plan ___ listo, pero los recursos aun no.",
        "options": ["esta", "es", "son"],
        "answer": "esta",
        "explanation": "Estados temporales usan estar.",
        "examples": ["El equipo esta listo.", "La sala esta ocupada."],
        "category": "copula",
    },
    {
        "focus": "Preposition choice",
        "prompt": "Depende ___ la aprobacion del comite.",
        "options": ["de", "en", "por"],
        "answer": "de",
        "explanation": "El verbo depender se construye con de.",
        "examples": ["Depende de ti.", "Depende del presupuesto."],
        "category": "preposition",
    },
    {
        "focus": "Subjunctive trigger",
        "prompt": "Es importante que ___ a tiempo.",
        "options": ["llegas", "llegues", "llegaste"],
        "answer": "llegues",
        "explanation": "Es importante que + subjuntivo.",
        "examples": ["Es necesario que vengas.", "Quiero que lo sepas."],
        "category": "subjunctive",
    },
    {
        "focus": "Object pronoun placement",
        "prompt": "___ lo dije claramente.",
        "options": ["Se lo", "Le lo", "Lo le"],
        "answer": "Se lo",
        "explanation": "Le + lo se transforma en se lo.",
        "examples": ["Se lo explique.", "Se lo dare manana."],
        "category": "clitic",
    },
    {
        "focus": "Por vs para",
        "prompt": "Estudia mucho ___ aprobar el examen.",
        "options": ["por", "para", "de"],
        "answer": "para",
        "explanation": "Para indica proposito u objetivo.",
        "examples": ["Trabajo para vivir.", "Lo hago para ayudarte."],
        "category": "preposition",
    },
    {
        "focus": "Preterite vs imperfect",
        "prompt": "Mientras ___ el informe, sono el telefono.",
        "options": ["escribi", "escribia", "he escrito"],
        "answer": "escribia",
        "explanation": "Imperfecto para accion de fondo interrumpida.",
        "examples": ["Llovia cuando sali.", "Dormia cuando llamaste."],
        "category": "tense",
    },
]

# ============== COMMON MISTAKES ==============

COMMON_MISTAKES = [
    {
        "pattern": "dependen en",
        "correction": "dependen de",
        "tag": "preposition",
        "explanation": "El verbo depender siempre va con de.",
        "examples": ["Depende de la aprobacion.", "Dependemos de su respuesta."],
    },
    {
        "pattern": "tomar una decision en",
        "correction": "tomar una decision sobre",
        "tag": "preposition",
        "explanation": "En espanol, tomar una decision sobre un tema es mas natural.",
        "examples": ["Tomamos una decision sobre el presupuesto.", "Tomo una decision sobre el contrato."],
    },
    {
        "pattern": "la problema",
        "correction": "el problema",
        "tag": "gender",
        "explanation": "Problema es masculino pese a terminar en -a.",
        "examples": ["El problema fue resuelto.", "El problema persiste."],
    },
    {
        "pattern": "aplicar para",
        "correction": "solicitar / presentarse a",
        "tag": "calque",
        "explanation": "Aplicar para es un calco del ingles apply for.",
        "examples": ["Solicite el puesto.", "Me presente a la convocatoria."],
    },
    {
        "pattern": "estoy excitado",
        "correction": "estoy emocionado / entusiasmado",
        "tag": "false_friend",
        "explanation": "Excitado tiene connotacion sexual en espanol.",
        "examples": ["Estoy muy emocionado.", "Me entusiasma la idea."],
    },
    {
        "pattern": "soportar (tolerar)",
        "correction": "aguantar / tolerar",
        "tag": "false_friend",
        "explanation": "Soportar significa tolerar, no apoyar (support).",
        "examples": ["No aguanto el ruido.", "Tolera bien la presion."],
    },
    {
        "pattern": "realizar (darse cuenta)",
        "correction": "darse cuenta de",
        "tag": "false_friend",
        "explanation": "Realizar significa llevar a cabo, no darse cuenta.",
        "examples": ["Me di cuenta del error.", "Realizamos el proyecto."],
    },
    {
        "pattern": "actualmente (en realidad)",
        "correction": "en realidad / de hecho",
        "tag": "false_friend",
        "explanation": "Actualmente significa ahora mismo, no actually.",
        "examples": ["Actualmente vivo en Madrid.", "En realidad, no estoy de acuerdo."],
    },
]

# ============== VOCAB CONTEXT UNITS ==============

VOCAB_CONTEXT_UNITS = [
    {
        "term": "tomar una decision",
        "collocations": ["tomar una decision", "tomar una postura", "tomar medidas"],
        "contexts": [
            "Dialogo: —Ya resolviste lo del cambio de proveedor? —Si, tomamos una decision anoche.",
            "Mensaje: Tomamos una decision: renegociar el contrato esta semana.",
            "Parrafo: Tras revisar los datos, el comite tomo una decision estrategica para proteger el margen.",
        ],
        "question": "Quien tomo la decision en los ejemplos?",
        "cloze": {
            "sentence": "Despues de analizarlo, ___ una decision rapida.",
            "options": ["tomamos", "hicimos", "dimos"],
            "answer": "tomamos",
            "explanation": "Tomar es el verbo natural para decisiones en espanol.",
        },
        "scenario": "Escribe una frase en la que decidas algo en un contexto laboral.",
        "swap": {"base": "Tomamos una decision prudente para evitar el riesgo.", "choices": ["medida", "postura", "ruta"]},
    },
    {
        "term": "me da la sensacion de que",
        "collocations": ["me da la sensacion de que", "me da la impresion de que", "tengo la sensacion de que"],
        "contexts": [
            "Dialogo: Me da la sensacion de que el cliente esta dudando.",
            "Mensaje: Me da la sensacion de que llegaremos tarde si no salimos ya.",
            "Parrafo: Me da la sensacion de que el equipo necesita mas claridad en los objetivos.",
        ],
        "question": "Que indica la frase: certeza o percepcion?",
        "cloze": {
            "sentence": "___ no estan totalmente convencidos de la propuesta.",
            "options": ["Me da la sensacion de que", "Estoy seguro de que", "Confirmo que"],
            "answer": "Me da la sensacion de que",
            "explanation": "La frase indica percepcion, no certeza absoluta.",
        },
        "scenario": "Escribe una frase que exprese intuicion sobre un proyecto.",
        "swap": {"base": "Me da la sensacion de que el plan es viable.", "choices": ["posible", "arriesgado", "inviable"]},
    },
    {
        "term": "llevar a cabo",
        "collocations": ["llevar a cabo", "llevar adelante", "llevar a termino"],
        "contexts": [
            "Dialogo: —Pudieron llevar a cabo el proyecto? —Si, terminamos la semana pasada.",
            "Mensaje: Vamos a llevar a cabo la reunion manana a las 10.",
            "Parrafo: El equipo logro llevar a cabo todas las fases del plan sin contratiempos.",
        ],
        "question": "Que tipo de acciones se llevan a cabo?",
        "cloze": {
            "sentence": "Decidimos ___ el plan original sin modificaciones.",
            "options": ["llevar a cabo", "hacer", "pensar"],
            "answer": "llevar a cabo",
            "explanation": "Llevar a cabo implica ejecutar algo complejo de principio a fin.",
        },
        "scenario": "Escribe una frase sobre ejecutar un plan o estrategia.",
        "swap": {"base": "Llevamos a cabo el proyecto con exito.", "choices": ["plan", "estrategia", "investigacion"]},
    },
]

# ============== CONVERSATION SCENARIOS ==============

CONVERSATION_SCENARIOS = [
    {
        "title": "Negociar un reembolso",
        "brief": "El servicio fallo y necesitas un reembolso parcial sin romper la relacion.",
        "hidden_targets": [
            "Usa 2 mitigadores (quiza, tal vez, me parece).",
            "Incluye una concesion (aunque, si bien).",
            "Evita 'aplicar para' como calco.",
        ],
        "opening": "Buenas tardes. Queria hablar sobre el servicio del mes pasado...",
        "system_role": "customer_service",
    },
    {
        "title": "Resolver un conflicto en el trabajo",
        "brief": "Un colega no cumplio plazos y necesitas renegociar el cronograma.",
        "hidden_targets": [
            "Usa 1 verbo preciso (afrontar, plantear, desactivar).",
            "Incluye una peticion indirecta (seria posible...?).",
            "Manten registro neutral-formal.",
        ],
        "opening": "Oye, queria hablar contigo sobre el proyecto...",
        "system_role": "colleague",
    },
    {
        "title": "Negociar un alquiler",
        "brief": "Quieres negociar el precio del alquiler con argumentos solidos.",
        "hidden_targets": [
            "Usa registro formal con usted.",
            "Incluye 2 frases de cortesia.",
            "Menciona datos o comparaciones concretas.",
        ],
        "opening": "Buenos dias. Le llamo por el piso que tiene en alquiler...",
        "system_role": "landlord",
    },
    {
        "title": "Pedir una extension de plazo",
        "brief": "Necesitas mas tiempo para un entregable sin parecer poco profesional.",
        "hidden_targets": [
            "Justifica con razones concretas.",
            "Ofrece una solucion parcial.",
            "Usa condicionales para suavizar.",
        ],
        "opening": "Hola, queria comentarte algo sobre el plazo del informe...",
        "system_role": "manager",
    },
    {
        "title": "Queja formal en un hotel",
        "brief": "Tu habitacion tiene problemas y quieres solucion y compensacion.",
        "hidden_targets": [
            "Mantén tono firme pero educado.",
            "Enumera los problemas claramente.",
            "Pide compensacion especifica.",
        ],
        "opening": "Disculpe, necesito hablar con el encargado sobre mi habitacion...",
        "system_role": "hotel_staff",
    },
]

# ============== DAILY MISSION TEMPLATES ==============

DAILY_MISSION_TEMPLATES = [
    {
        "type": "speaking",
        "title": "Update de proyecto",
        "prompt": "Graba un update de 60-90 segundos explicando el estado de un proyecto ficticio. Menciona un obstaculo y como lo afrontaste.",
        "constraints": ["Usa 2 verbos del banco: sopesar, afrontar, plantear, desactivar",
                       "Incluye un conector concesivo (aunque, si bien)",
                       "Usa vocabulario del dominio profesional"],
        "vocab_focus": ["sopesar", "afrontar", "plantear"],
        "grammar_focus": "conectores concesivos",
    },
    {
        "type": "writing",
        "title": "Email de negociacion",
        "prompt": "Escribe un email de 4-6 oraciones respondiendo a un cliente que pide mas alcance sin ampliar plazos.",
        "constraints": ["Usa 1 verbo de negociacion (pactar, ceder, plantear)",
                       "Incluye una frase de mitigacion (quiza, tal vez, me parece)",
                       "Evita calcos del ingles"],
        "vocab_focus": ["pactar", "plantear", "mitigacion"],
        "grammar_focus": "condicionales para cortesia",
    },
    {
        "type": "speaking",
        "title": "Explicar un problema medico",
        "prompt": "Graba 60-90 segundos explicando sintomas a un medico de forma clara y organizada.",
        "constraints": ["Usa vocabulario del dominio salud",
                       "Organiza cronologicamente",
                       "Incluye un subjuntivo con recomendacion"],
        "vocab_focus": ["sintoma", "diagnostico", "consulta"],
        "grammar_focus": "subjuntivo con expresiones de consejo",
    },
    {
        "type": "writing",
        "title": "Reclamacion formal",
        "prompt": "Escribe 4-6 oraciones reclamando un retraso en un envio. Se firme pero cortes.",
        "constraints": ["Usa registro formal con usted",
                       "Incluye fechas y datos concretos",
                       "Pide solucion especifica"],
        "vocab_focus": ["reclamar", "plazo", "indemnizacion"],
        "grammar_focus": "condicionales de cortesia",
    },
    {
        "type": "speaking",
        "title": "Desacuerdo diplomatico",
        "prompt": "Graba 60-90 segundos expresando desacuerdo con una propuesta de un colega sin crear tension.",
        "constraints": ["Usa 2 suavizadores (quiza, me parece, tal vez)",
                       "Incluye una concesion antes del desacuerdo",
                       "Propón una alternativa"],
        "vocab_focus": ["plantear", "considerar", "alternativa"],
        "grammar_focus": "hedging y mitigacion",
    },
]

# ============== REGISTER MARKERS ==============

REGISTER_MARKERS = {
    "politeness": ["por favor", "le agradeceria", "quisiera", "seria posible", "disculpe", "perdone"],
    "hedging": ["quiza", "tal vez", "podria", "seria", "me parece", "a mi modo de ver", "diria que"],
    "direct": ["necesito", "exijo", "debe", "quiero", "hay que", "tiene que"],
    "idiomatic": ["me da la impresion", "en pocas palabras", "a fin de cuentas", "de hecho", "por cierto"],
    "academic": ["objetivo", "metodologia", "resultados", "conclusion", "se analiza", "cabe destacar"],
    "whatsapp": ["jaja", "que tal", "oye", "vale", "ok", "genial", "bueno"],
    "pitch": ["propuesta", "impacto", "beneficio", "valor", "oportunidad", "solucion"],
}

# ============== DIALECTS ==============

DIALECT_MODULES = {
    "Spain": {
        "features": ["distincion entre /θ/ y /s/", "leismo moderado", "tu predominante"],
        "lexicon": {"ordenador": "computer", "coger": "to take/grab", "vale": "okay", "mola": "it's cool"},
        "sample": "Vale, luego te llamo para concretar los detalles.",
        "trap": {"question": "Que matiz tiene 'vale' aqui?",
                 "options": ["confirmacion informal", "desacuerdo", "sorpresa"], "answer": "confirmacion informal"},
    },
    "Mexico": {
        "features": ["seseo", "ustedes generalizado", "diminutivos frecuentes"],
        "lexicon": {"computadora": "computer", "platicar": "to chat", "ahorita": "right now (flexible)", "padre": "cool"},
        "sample": "Ahorita lo revisamos y te aviso.",
        "trap": {"question": "Que implica 'ahorita' en este contexto?",
                 "options": ["inmediatamente", "pronto pero flexible", "manana"], "answer": "pronto pero flexible"},
    },
    "Argentina": {
        "features": ["voseo", "yeismo rehilado", "entonacion italiana"],
        "lexicon": {"vos": "you (informal)", "laburo": "work", "che": "hey", "boludo": "dude"},
        "sample": "Che, vos venis a la reunion o laburas desde casa?",
        "trap": {"question": "Que marca el uso de 'vos'?",
                 "options": ["voseo", "formalidad", "plural"], "answer": "voseo"},
    },
    "Colombia": {
        "features": ["ustedeo frecuente", "diminutivos", "entonacion melodica"],
        "lexicon": {"sumerce": "usted (Boyaca)", "parce": "buddy", "chevere": "cool", "tinto": "black coffee"},
        "sample": "Que chevere que pudo venir, parce.",
        "trap": {"question": "Que significa 'chevere'?",
                 "options": ["dificil", "agradable/genial", "rapido"], "answer": "agradable/genial"},
    },
    "Chile": {
        "features": ["aspiracion de /s/", "vocabulario muy local", "habla rapida"],
        "lexicon": {"pololo/a": "boyfriend/girlfriend", "fome": "boring", "cachai": "you know?", "po": "pues"},
        "sample": "Oye, cachai que paso con el proyecto, po?",
        "trap": {"question": "Que funcion cumple 'po'?",
                 "options": ["negacion", "enfasis", "pregunta"], "answer": "enfasis"},
    },
}

# ============== PLACEMENT TEST ==============

PLACEMENT_QUESTIONS = [
    {
        "level": "B2",
        "type": "grammar",
        "question": "Si ___ antes, habriamos llegado a tiempo.",
        "options": ["salimos", "salieramos", "hubieramos salido", "habiamos salido"],
        "answer": "hubieramos salido",
        "skill": "conditional_perfect",
    },
    {
        "level": "C1",
        "type": "vocabulary",
        "question": "El proyecto requiere ___ los riesgos cuidadosamente.",
        "options": ["mirar", "ver", "sopesar", "observar"],
        "answer": "sopesar",
        "skill": "verb_precision",
    },
    {
        "level": "C1",
        "type": "collocation",
        "question": "Necesitamos ___ una decision pronto.",
        "options": ["hacer", "tomar", "dar", "poner"],
        "answer": "tomar",
        "skill": "collocation",
    },
    {
        "level": "C1",
        "type": "register",
        "question": "Cual es mas apropiado en un email formal?",
        "options": ["Oye, necesito que...", "Le agradeceria que...", "Tienes que...", "Quiero que..."],
        "answer": "Le agradeceria que...",
        "skill": "register",
    },
    {
        "level": "C2",
        "type": "nuance",
        "question": "'Me da la sensacion de que' expresa:",
        "options": ["certeza absoluta", "percepcion subjetiva", "orden directa", "pregunta retorica"],
        "answer": "percepcion subjetiva",
        "skill": "pragmatics",
    },
    {
        "level": "C1",
        "type": "preposition",
        "question": "El resultado depende ___ varios factores.",
        "options": ["en", "de", "por", "con"],
        "answer": "de",
        "skill": "preposition",
    },
    {
        "level": "C2",
        "type": "discourse",
        "question": "Para contrastar ideas, cual es mejor?",
        "options": ["Ademas", "Sin embargo", "Por lo tanto", "Es decir"],
        "answer": "Sin embargo",
        "skill": "discourse_markers",
    },
    {
        "level": "B2",
        "type": "grammar",
        "question": "Quiero que ___ a la reunion.",
        "options": ["vienes", "vengas", "venias", "vendras"],
        "answer": "vengas",
        "skill": "subjunctive",
    },
]
