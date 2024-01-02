<template>
<a onclick="history.back()" class="previous">&#8249;</a>
<p class="maincon"> Listed below are diffrent hotlines. </p>
  <div class="hotline">
      
    <p> Suicide prevention hotline: <a href="tel:800-273-8255">800-273-8255</a> </p>
    <p> Suicide prevention hotline español: <a href="tel:888-628-9454">888-628-9454</a> </p>
    <p> Substance abuse and mental health hotline English and español: <a href="tel:800-487-4889">800-487-4889</a> </p>
    <p> Crisis textline: <a href="tel:800-273-8255">800-273-8255</a> </p>
    <!-- translate above into spanish -->
    <p> Domestic violence hotline: <a href="tel:800.799.7233">800.799.7233</a> </p>
    <p> Veterans crisis hotline: <a href="tel:800-273-8255">800-273-8255</a> </p>
    <p> Sexual assault hotline: <a href="tel:800-656-4673">800-656-4673</a> </p>
    <p> HIV hotline: <a href="tel:888-232-6348">888-232-6348</a> </p>
  </div>
</template>
<script>

export default {
  name: "Hotlines",
  methods: {
   
  }
}
</script>
<style scoped>
.hotline{
  font-family: Arial, Helvetica, sans-serif;
  position: absolute;
  color: black;
  top: 5em;
  left: 2rem;
  text-align: left;
}
</style>