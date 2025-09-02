// API Principal para Cloudflare Functions
// Archivo: functions/api/[[path]].js

export async function onRequest(context) {
    const { request, env, params } = context;
    const url = new URL(request.url);
    const path = params.path?.join('/') || '';

    // Configurar CORS
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    // Manejar preflight requests
    if (request.method === 'OPTIONS') {
        return new Response(null, { headers: corsHeaders });
    }

    try {
        // Router para diferentes endpoints
        switch (true) {
            case path === 'patients' && request.method === 'GET':
                return handleGetPatients(context);

            case path === 'patients' && request.method === 'POST':
                return handleCreatePatient(context);

            case path.startsWith('patients/') && request.method === 'GET':
                const patientId = path.split('/')[1];
                return handleGetPatient(context, patientId);

            case path === 'alerts' && request.method === 'GET':
                return handleGetAlerts(context);

            case path === 'labs' && request.method === 'POST':
                return handleCreateLab(context);

            case path === 'sessions' && request.method === 'POST':
                return handleCreateSession(context);

            default:
                return new Response('Endpoint not found', { 
                    status: 404, 
                    headers: corsHeaders 
                });
        }
    } catch (error) {
        console.error('API Error:', error);
        return new Response(JSON.stringify({ error: 'Internal Server Error' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}

// Obtener todos los pacientes
async function handleGetPatients(context) {
    const { env } = context;

    try {
        // Si no hay base de datos D1, retornar datos de ejemplo
        if (!env.DB) {
            const samplePatients = [
                {
                    id: 1,
                    documento: 'CC 12345678',
                    tipo_documento: 'CC',
                    nombres: 'María Elena',
                    apellidos: 'González López',
                    edad: 58,
                    genero: 'F',
                    eps: 'Nueva EPS',
                    fecha_inicio_hd: '2022-06-10',
                    causa_erc: 'Diabetes Mellitus tipo 2',
                    activo: true,
                    tiempo_dialisis_meses: 18
                },
                {
                    id: 2,
                    documento: 'CC 87654321',
                    tipo_documento: 'CC',
                    nombres: 'Carlos Andrés',
                    apellidos: 'Rodríguez Martín',
                    edad: 65,
                    genero: 'M',
                    eps: 'Sanitas EPS',
                    fecha_inicio_hd: '2021-11-05',
                    causa_erc: 'Nefropatía hipertensiva',
                    activo: true,
                    tiempo_dialisis_meses: 22
                },
                {
                    id: 3,
                    documento: 'CC 45678912',
                    tipo_documento: 'CC',
                    nombres: 'Ana Lucia',
                    apellidos: 'Pérez Silva',
                    edad: 51,
                    genero: 'F',
                    eps: 'SURA EPS',
                    fecha_inicio_hd: '2023-01-18',
                    causa_erc: 'Glomerulonefritis crónica',
                    activo: true,
                    tiempo_dialisis_meses: 8
                }
            ];

            return new Response(JSON.stringify(samplePatients), {
                headers: { 
                    ...corsHeaders, 
                    'Content-Type': 'application/json' 
                }
            });
        }

        // Consulta a base de datos D1
        const result = await env.DB.prepare(
            'SELECT * FROM pacientes WHERE activo = 1 ORDER BY nombres, apellidos'
        ).all();

        return new Response(JSON.stringify(result.results), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Error getting patients:', error);
        return new Response(JSON.stringify({ error: 'Error retrieving patients' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}

// Crear nuevo paciente
async function handleCreatePatient(context) {
    const { request, env } = context;

    try {
        const patientData = await request.json();

        // Validaciones básicas
        if (!patientData.documento || !patientData.nombres || !patientData.apellidos) {
            return new Response(JSON.stringify({ 
                error: 'Campos obligatorios: documento, nombres, apellidos' 
            }), {
                status: 400,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (!env.DB) {
            // Simular creación exitosa
            const newPatient = {
                id: Date.now(),
                ...patientData,
                activo: true,
                fecha_registro: new Date().toISOString()
            };

            return new Response(JSON.stringify(newPatient), {
                status: 201,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        // Insertar en base de datos D1
        const result = await env.DB.prepare(`
            INSERT INTO pacientes (
                documento, tipo_documento, nombres, apellidos, 
                fecha_nacimiento, genero, telefono, direccion, 
                eps, fecha_inicio_hd, causa_erc, comorbilidades, 
                activo, fecha_registro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, datetime('now'))
        `).bind(
            patientData.documento,
            patientData.tipo_documento,
            patientData.nombres,
            patientData.apellidos,
            patientData.fecha_nacimiento,
            patientData.genero,
            patientData.telefono || null,
            patientData.direccion || null,
            patientData.eps || null,
            patientData.fecha_inicio_hd,
            patientData.causa_erc || null,
            patientData.comorbilidades || null
        ).run();

        if (result.success) {
            const newPatient = {
                id: result.meta.last_row_id,
                ...patientData,
                activo: true
            };

            return new Response(JSON.stringify(newPatient), {
                status: 201,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        } else {
            throw new Error('Failed to create patient');
        }

    } catch (error) {
        console.error('Error creating patient:', error);
        return new Response(JSON.stringify({ error: 'Error creating patient' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}

// Obtener paciente específico
async function handleGetPatient(context, patientId) {
    const { env } = context;

    try {
        if (!env.DB) {
            // Datos de ejemplo para paciente específico
            const samplePatient = {
                id: parseInt(patientId),
                documento: 'CC 12345678',
                nombres: 'María Elena',
                apellidos: 'González López',
                edad: 58,
                genero: 'F',
                eps: 'Nueva EPS',
                laboratorios: [
                    {
                        fecha: '2024-01-15',
                        hemoglobina: 10.2,
                        ferritina: 280,
                        calcio: 9.1,
                        fosforo: 4.8,
                        pth: 220
                    }
                ],
                sesiones: [
                    {
                        fecha: '2024-01-20',
                        kt_v: 1.4,
                        pru: 72,
                        peso_pre: 72.5,
                        peso_post: 69.8
                    }
                ]
            };

            return new Response(JSON.stringify(samplePatient), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        // Consulta con joins para obtener datos completos
        const patient = await env.DB.prepare(`
            SELECT p.*, 
                   l.hemoglobina, l.ferritina, l.calcio, l.fosforo, l.pth,
                   s.kt_v, s.pru, s.peso_pre, s.peso_post
            FROM pacientes p
            LEFT JOIN laboratorios l ON p.id = l.paciente_id
            LEFT JOIN sesiones_dialisis s ON p.id = s.paciente_id
            WHERE p.id = ? AND p.activo = 1
            ORDER BY l.fecha DESC, s.fecha DESC
            LIMIT 1
        `).bind(patientId).first();

        if (!patient) {
            return new Response(JSON.stringify({ error: 'Patient not found' }), {
                status: 404,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        return new Response(JSON.stringify(patient), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Error getting patient:', error);
        return new Response(JSON.stringify({ error: 'Error retrieving patient' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}

// Obtener alertas
async function handleGetAlerts(context) {
    const { env } = context;

    try {
        if (!env.DB) {
            // Alertas de ejemplo
            const sampleAlerts = [
                {
                    id: 1,
                    paciente_id: 1,
                    tipo: 'CRITICA',
                    categoria: 'ANEMIA',
                    mensaje: 'Hemoglobina crítica: 7.8 g/dl. Considerar transfusión urgente.',
                    fecha_creacion: new Date().toISOString(),
                    paciente_nombre: 'María Elena González López',
                    prioridad: 5
                },
                {
                    id: 2,
                    paciente_id: 2,
                    tipo: 'MODERADA',
                    categoria: 'MINERAL_OSEO',
                    mensaje: 'PTH elevada: 420 pg/ml. Revisar dosis de vitamina D.',
                    fecha_creacion: new Date().toISOString(),
                    paciente_nombre: 'Carlos Andrés Rodríguez Martín',
                    prioridad: 3
                },
                {
                    id: 3,
                    paciente_id: 3,
                    tipo: 'PREVENTIVA',
                    categoria: 'ACCESO_VASCULAR',
                    mensaje: 'Riesgo de disfunción de acceso: 78%. Programar evaluación vascular.',
                    fecha_creacion: new Date().toISOString(),
                    paciente_nombre: 'Ana Lucia Pérez Silva',
                    prioridad: 2
                }
            ];

            return new Response(JSON.stringify(sampleAlerts), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        // Consulta a base de datos D1
        const result = await env.DB.prepare(`
            SELECT a.*, p.nombres || ' ' || p.apellidos as paciente_nombre
            FROM alertas a
            JOIN pacientes p ON a.paciente_id = p.id
            WHERE a.resuelta = 0
            ORDER BY a.prioridad DESC, a.fecha_creacion DESC
            LIMIT 50
        `).all();

        return new Response(JSON.stringify(result.results), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Error getting alerts:', error);
        return new Response(JSON.stringify({ error: 'Error retrieving alerts' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}

// Crear laboratorio
async function handleCreateLab(context) {
    const { request, env } = context;

    try {
        const labData = await request.json();

        if (!env.DB) {
            return new Response(JSON.stringify({ 
                id: Date.now(), 
                ...labData, 
                fecha: new Date().toISOString() 
            }), {
                status: 201,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        const result = await env.DB.prepare(`
            INSERT INTO laboratorios (
                paciente_id, fecha, hemoglobina, hematocrito, ferritina, 
                tsat, hierro_serico, pcr, calcio, fosforo, pth, vitamina_d
            ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(
            labData.paciente_id,
            labData.hemoglobina,
            labData.hematocrito,
            labData.ferritina,
            labData.tsat,
            labData.hierro_serico,
            labData.pcr,
            labData.calcio,
            labData.fosforo,
            labData.pth,
            labData.vitamina_d
        ).run();

        if (result.success) {
            return new Response(JSON.stringify({ 
                id: result.meta.last_row_id, 
                ...labData 
            }), {
                status: 201,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

    } catch (error) {
        console.error('Error creating lab:', error);
        return new Response(JSON.stringify({ error: 'Error creating lab result' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}

// Crear sesión de diálisis
async function handleCreateSession(context) {
    const { request, env } = context;

    try {
        const sessionData = await request.json();

        if (!env.DB) {
            return new Response(JSON.stringify({ 
                id: Date.now(), 
                ...sessionData, 
                fecha: new Date().toISOString() 
            }), {
                status: 201,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        const result = await env.DB.prepare(`
            INSERT INTO sesiones_dialisis (
                paciente_id, fecha, turno, peso_pre, peso_post, peso_seco,
                qb, tiempo_sesion, uf_programada, uf_real, kt_v, pru
            ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(
            sessionData.paciente_id,
            sessionData.turno,
            sessionData.peso_pre,
            sessionData.peso_post,
            sessionData.peso_seco,
            sessionData.qb,
            sessionData.tiempo_sesion,
            sessionData.uf_programada,
            sessionData.uf_real,
            sessionData.kt_v,
            sessionData.pru
        ).run();

        if (result.success) {
            return new Response(JSON.stringify({ 
                id: result.meta.last_row_id, 
                ...sessionData 
            }), {
                status: 201,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

    } catch (error) {
        console.error('Error creating session:', error);
        return new Response(JSON.stringify({ error: 'Error creating dialysis session' }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}