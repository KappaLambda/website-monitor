<template>
  <div class="col-lg-8 col-md-10">
    <div class="home">
      <h1 class="m-3">Welcome to Website Monitor API!</h1>
      <p class="m-3">A RESTful API using Django Rest Framework and Vuejs.</p>
      <p class="m-3">Log in to use it or check for more info on<a id="github-link" href="https://github.com/KappaLambda/website-monitor"><font-awesome-icon :icon="['fab', 'github']" class="mx-1"/>GitHub</a>.</p>
    </div>
  </div>
</template>

<script>
export default {

}
</script>

<style scoped>
.home {
  margin-top: 1em;
  margin-bottom: 1em;
  text-align: center;
}

#github-link {
  color: black;
}

#github-link:hover {
  color: blue;
  text-decoration: none;

}
</style>
