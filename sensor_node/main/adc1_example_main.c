/* ADC1 Example
bt09201 datasheet
   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/adc.h"
#include "esp_adc_cal.h"

#include "time.h"
#include "sys/time.h"
#include "driver/gpio.h"

#define DEFAULT_VREF    1100        //Use adc2_vref_to_gpio() to obtain a better estimate
#define MICROPHONE 0
#define PIR 1
#define SENSOR_TYPE MICROPHONE

#define INPUT_GPIO 12
#define ESP_INR_FLAG_DEFAULT 0

static esp_adc_cal_characteristics_t *adc_chars;
static const adc_channel_t channel = ADC_CHANNEL_4;     //GPIO34 if ADC1, GPIO14 if ADC2
static const adc_atten_t atten = ADC_ATTEN_6db;
static const adc_unit_t unit = ADC_UNIT_2;

static int event_flag;

//static struct timeval freq_start;
//static struct timeval tv_start, tv_now;
//static int64_t elapsed;

static void IRAM_ATTR gpio_isr_handler(void* arg){
    event_flag = 1;
}

static void check_efuse(void)
{
    //Check TP is burned into eFuse
    if (esp_adc_cal_check_efuse(ESP_ADC_CAL_VAL_EFUSE_TP) == ESP_OK) {
        printf("eFuse Two Point: Supported\n");
    } else {
        printf("eFuse Two Point: NOT supported\n");
    }

    //Check Vref is burned into eFuse
    if (esp_adc_cal_check_efuse(ESP_ADC_CAL_VAL_EFUSE_VREF) == ESP_OK) {
        printf("eFuse Vref: Supported\n");
    } else {
        printf("eFuse Vref: NOT supported\n");
    }
}

static void print_char_val_type(esp_adc_cal_value_t val_type)
{
    if (val_type == ESP_ADC_CAL_VAL_EFUSE_TP) {
        printf("Characterized using Two Point Value\n");
    } else if (val_type == ESP_ADC_CAL_VAL_EFUSE_VREF) {
        printf("Characterized using eFuse Vref\n");
    } else {
        printf("Characterized using Default Vref\n");
    }
}

void app_main(void)
{
    gpio_config_t io_config;
    
    //Configure Button Input
    io_config.intr_type = GPIO_INTR_DISABLE;
    io_config.mode = GPIO_MODE_INPUT;
    io_config.pin_bit_mask = 1ULL;
    gpio_config(&io_config);

    //Configure event trigger  input
    #if (SENSOR_TYPE == MICROPHONE)
    io_config.intr_type = GPIO_PIN_INTR_NEGEDGE;
    #else
    io_config.intr_type = GPIO_PIN_INTR_POSEDGE;
    #endif
    io_config.mode = GPIO_MODE_INPUT;
    io_config.pin_bit_mask = (1ULL << INPUT_GPIO);
    gpio_config(&io_config);

    //Configure event trigger interrupt
    gpio_install_isr_service(ESP_INR_FLAG_DEFAULT);
    gpio_isr_handler_add(INPUT_GPIO, gpio_isr_handler, (void *)INPUT_GPIO); 

    //Check if Two Point or Vref are burned into eFuse
    check_efuse();

    //Configure ADC
    if (unit == ADC_UNIT_1) {
        adc1_config_width(ADC_WIDTH_BIT_12);
        adc1_config_channel_atten(channel, atten);
    } else {
        adc2_config_channel_atten((adc2_channel_t)channel, atten);
    }

    //Characterize ADC
    adc_chars = calloc(1, sizeof(esp_adc_cal_characteristics_t));
    esp_adc_cal_value_t val_type = esp_adc_cal_characterize(unit, atten, ADC_WIDTH_BIT_12, DEFAULT_VREF, adc_chars);
    print_char_val_type(val_type);

    //Wait for button press
    while(gpio_get_level(0));
    while(!gpio_get_level(0));

    printf("Begin:\n");

    uint8_t shifted;
    int raw;
    struct timeval freq_start, tv_now;
    int64_t elapsed;
    event_flag = 0;

    while(1){
        if(event_flag){
    	    gettimeofday(&freq_start, NULL);
            putchar(0x00);
            do{
                adc2_get_raw((adc2_channel_t)channel, ADC_WIDTH_BIT_12, &raw);
                shifted = raw >> 4;
                putchar(0xAA);
                putchar(shifted);
                fflush(stdout);
                gettimeofday(&tv_now, NULL);
                elapsed = ((int64_t)tv_now.tv_sec - (int64_t)freq_start.tv_sec) * 1000000L + ((int64_t)tv_now.tv_usec - (int64_t)freq_start.tv_usec);
            }while(elapsed < 1000000L);
            putchar(0xFF);
            fflush(stdout);
	    event_flag = 0;
        }else vTaskDelay(1); 
    }
}
