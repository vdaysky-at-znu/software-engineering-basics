<template>
  <v-container>
    <v-row>
        <v-col>
            <h2>{{ post.title }}</h2>
            <h4>
                {{ post.subtitle }}
            </h4>
        </v-col>
        <v-col>
            <v-img v-if="post.header_image" cover :src="post.header_image" height="200px"></v-img>
        </v-col>
    </v-row>
    <v-row>
        <v-col>
            <p>{{ post.text }}</p>
        </v-col>
    </v-row>

  </v-container>
</template>

<script>
import { Post } from '@/api/model/models';
export default {

    data() {
        return {
            post: new Post(this.$route.params.id)
        }
    },
}
</script>

<style>

</style>