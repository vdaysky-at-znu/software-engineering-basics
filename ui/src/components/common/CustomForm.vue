<template>
  
    <v-form>
        <div v-for="field in fields" :key="field.name">

            <v-text-field
                v-if="field.type === 'text' || field.type === 'number' || field.type === 'email' || field.type === 'password'"
                :color="colors[field.name]"
                v-model="formData[field.name]"
                :label="field.label"
                :error-messages="errors[field.name]"
                :type="field.type || 'text'"
                :loading="inProgress[field.name] || false"
                @update:modelValue="e => onFieldUpdate(field, e)"
            >
            <template v-slot:appendInner="{}">
                <v-icon large v-if="icons[field.name]" :color="colors[field.name]">{{ icons[field.name] }}</v-icon>
            </template>
                
            </v-text-field>

            <div v-if="field.type == 'date'">
                <p>{{ field.label }}</p>
                <v-datepicker 
                v-model="formData[field.name]"
                @update:modelValue="e => onFieldUpdate(field, e)"
            >
                </v-datepicker>

                <div class="v-input__details">
                    <div class="v-messages">
                        <div class="v-messages__message" style="color: rgb(var(--v-theme-error))">
                        {{ errors[field.name] }}  
                        </div>
                    </div>
                </div>
            </div>
            
            <v-select
                v-if="field.type == 'select'"
                v-model="formData[field.name]"
                :label="field.label"
                :items="field.options"
            >

            </v-select>
            
        </div>
        
    </v-form>

</template>

<script>
export default {
    props: ['fields', 'modelValue'],
    data: function(){
        return {
        formData: this.modelValue,
        errors: {},
        icons: {},
        colors: {},
        inProgress: {},
    }},

    watch: {

        formData: {
            handler: async function (newVal) {
                this.$emit('update:formData', newVal);
            },
            deep: true,
        },
    },

    methods: {

        reset() { 
            this.formData = {};
            this.errors = {};
            this.icons = {};
            this.colors = {};
            this.inProgress = {};
            this.$emit('update:modelValue', this.formData);
        },

        onFieldUpdate(field, e) {
            this.validateField(field);
            let event = field.name + "Update";
            this.$emit(event, e);
        },
        async validateField(field) {
            this.errors[field.name] = undefined;

            if (field.required && !this.formData[field.name]) {
                this.errors[field.name] = 'This field is required';
                this.icons[field.name] = "mdi-alert-circle";
                this.colors[field.name] = "error";
                return false;
            }

            if (field.validators?.length) {
                this.inProgress[field.name] = true;
                for (let validator of field.validators) {

                    let validatorResult = validator(this.formData[field.name]);

                    console.log("validator res", validatorResult);
                    if (validatorResult instanceof Promise) {
                            console.log("wait promise");
                        validatorResult = await validatorResult;
                        console.log("promise res", validatorResult);
                    }

                    if (typeof validatorResult === 'string') {
                        this.errors[field.name] = validatorResult;
                        this.icons[field.name] = "mdi-alert-circle";
                        this.inProgress[field.name] = false;
                        this.colors[field.name] = "error";
                        // this field is invalid, no need to further valdiate
                        break;
                    }
                    this.inProgress[field.name] = false;
                    this.icons[field.name] = "mdi-check-circle";
                    this.colors[field.name] = "success";
                }
            }
        },
        async validateAll() {
            for (let field of this.fields) {
                await this.validateField(field);
            }
            return Object.keys(this.errors).length === 0;
        },
    },
}
</script>

<style>

</style>