<template>
<v-container>
  <v-row v-for="post in articles" :key="post.id">
    <v-col>
      <v-card>
        <v-img v-if="post.header_image" cover :src="post.header_image" height="200px"></v-img>
        <v-card-title>
          {{ post.title }}
        </v-card-title>
        <v-card-subtitle>
          {{ post.subtitle}}
        </v-card-subtitle>
        <v-card-content>
          {{ post.text }}
        </v-card-content>
        <v-card-actions>
          <v-btn :to="{name: 'post', params: {id: post.id} }">Read More</v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
  <v-row>
    <v-pagination :v-model="page">

    </v-pagination>
  </v-row>
</v-container>
</template>

<script>
import { Post } from '@/api/model/models';
import { defineComponent } from 'vue';


export default defineComponent({
  name: 'HomeView',
  data() { 
    return {
      articles: Post.all(),
      page: 0,
    }
  },
  components: {
  },
});
</script>
