<template>
  <v-container>
        <v-table>
            <thead>
                <tr>
                    <th class="text-left">
                        Event
                    </th>
                    <th class="text-right">
                        Start Date
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="event in events" :key="event.id">
                    <td>
                        <event-widget :event="event"></event-widget>
                    </td>
                    <td class="text-end">
                        {{ event.start_date }}
                    </td>
                </tr>
            </tbody>
        </v-table>
  </v-container>
</template>

<script>
import EventWidget from "../widgets/EventWidget.vue"

export default {
    props: ['events'],
    components: { EventWidget },
}
</script>

<style>

</style>