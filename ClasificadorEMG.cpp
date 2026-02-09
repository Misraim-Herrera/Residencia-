

#include <stdio.h>
#include <stdlib.h>
#include <math.h>       
#include <cstdint>      
#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "hardware/gpio.h"
#include <vector>

// --- CONFIGURACIÓN DE HARDWARE ---
#define ADC_PIN 26          
#define ADC_CHANNEL 0
#define SAMPLING_PERIOD_US 1000 // 1000Hz 
#define WINDOW_SIZE 200     // Ventana de 200ms para calcular MAD

const uint LED_BAJO = 16;
const uint LED_MEDIO = 18;
const uint LED_ALTO = 20;
const uint TODOS_LOS_LEDS[] = {16, 17, 18, 19, 20}; 

// UMBRALES DE ENERGÍA

const float UMBRAL_MEDIO = 30.0f;   
const float UMBRAL_ALTO = 80.0f;    

std::vector<float> buffer_lecturas;


// SECCIÓN DE FILTROS DIGITALES (DSP)

// COEFICIENTES FILTRO NOTCH (60Hz @ 1000Hz)
const double n_b0 = 0.99375596;
const double n_b1 = -1.84794186;
const double n_b2 = 0.99375596;
const double n_a1 = -1.84794186;
const double n_a2 = 0.98751193;

// Variables de estado para Notch
double nx1=0, nx2=0, ny1=0, ny2=0; 

//COEFICIENTES FILTRO PASABANDA (20-450Hz @ 1000Hz)
const double p_b0 = 0.73202248;
const double p_b1 = 0.0;
const double p_b2 = -1.46404495;
const double p_b3 = 0.0;
const double p_b4 = 0.73202248;

const double p_a1 = -0.26277146;
const double p_a2 = -1.36366734;
const double p_a3 = 0.13654262;
const double p_a4 = 0.53719462;

// Variables de estado para Pasabanda
double px1=0, px2=0, px3=0, px4=0;
double py1=0, py2=0, py3=0, py4=0;

// FUNCIÓN DE FILTRADO 
float aplicar_filtros(float entrada_raw) {
    // --- ETAPA 1: NOTCH (Eliminar 60Hz) ---
    // Ecuación: y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
    double x = (double)entrada_raw;
    double y_notch = (n_b0 * x) + (n_b1 * nx1) + (n_b2 * nx2) 
                   - (n_a1 * ny1) - (n_a2 * ny2);
    
    // Actualizar historial Notch
    nx2 = nx1; nx1 = x;
    ny2 = ny1; ny1 = y_notch;

    //  ETAPA 2: PASABANDA (20-450Hz) 
    // La entrada de este filtro es la salida del anterior (y_notch)
    double x_p = y_notch; 
    double y_band = (p_b0 * x_p) + (p_b1 * px1) + (p_b2 * px2) + (p_b3 * px3) + (p_b4 * px4)
                  - (p_a1 * py1) - (p_a2 * py2) - (p_a3 * py3) - (p_a4 * py4);

    // Actualizar historial Pasabanda
    px4 = px3; px3 = px2; px2 = px1; px1 = x_p;
    py4 = py3; py3 = py2; py2 = py1; py1 = y_band;

    return (float)y_band;
}

//LÓGICA DE LEDS 
void encender_led_estable(int clase) {
    static int historial[5] = {0}; 
    static int indice = 0;
    historial[indice] = clase;
    indice = (indice + 1) % 5;
    int votos[3] = {0, 0, 0}; 
    for(int i=0; i<5; i++) if(historial[i] >= 0 && historial[i] < 3) votos[historial[i]]++;

    int ganador = -1;
    if(votos[0] >= 3) ganador = 0;
    else if(votos[1] >= 3) ganador = 1;
    else if(votos[2] >= 3) ganador = 2;

    if (ganador != -1) {
        gpio_put(LED_BAJO, 0); gpio_put(LED_MEDIO, 0); gpio_put(LED_ALTO, 0);
        if (ganador == 0) gpio_put(LED_BAJO, 1);
        if (ganador == 1) gpio_put(LED_MEDIO, 1);
        if (ganador == 2) gpio_put(LED_ALTO, 1);
    }
}

int main() {
    stdio_init_all();
    adc_init();
    adc_gpio_init(ADC_PIN);
    adc_select_input(ADC_CHANNEL);

    for(int pin : TODOS_LOS_LEDS) {
        gpio_init(pin); gpio_set_dir(pin, GPIO_OUT); gpio_put(pin, 0);
    }

    // Blink de inicio
    for(int i=0; i<3; i++) { gpio_put(LED_MEDIO, 1); sleep_ms(100); gpio_put(LED_MEDIO, 0); sleep_ms(100); }

    uint64_t last_sample_time = time_us_64();

    while (true) {
        uint64_t current_time = time_us_64();

        if (current_time - last_sample_time >= SAMPLING_PERIOD_US) {
            last_sample_time += SAMPLING_PERIOD_US;

            // 1. LEER SENSOR
            uint16_t raw = adc_read();
            float lectura_raw = (float)raw * 1.0f; 

            // 2. APLICACIÓN DE FILTROS DIGITALES 
            float lectura_filtrada = aplicar_filtros(lectura_raw);

            // 3. BUFFER
            if (buffer_lecturas.size() >= WINDOW_SIZE) {
                buffer_lecturas.erase(buffer_lecturas.begin());
            }
            buffer_lecturas.push_back(lectura_filtrada);

            // 4. PROCESAR
            if (buffer_lecturas.size() == WINDOW_SIZE) {
                
                // Calcular Energía (MAD)
                float suma_total = 0;
                for(float val : buffer_lecturas) suma_total += val;
                float linea_base = suma_total / WINDOW_SIZE;

                float suma_diff = 0;
                for(float val : buffer_lecturas) suma_diff += fabsf(val - linea_base);
                float energia = suma_diff / WINDOW_SIZE;

                // 5. CLASIFICACIÓN
                int clase = 0; 
                if (energia > UMBRAL_ALTO) clase = 2; 
                else if (energia > UMBRAL_MEDIO) clase = 1; 
                else clase = 0;

                printf("Energia:%.2f\n", energia);

                encender_led_estable(clase);
            }
        }
    }
    return 0;
}