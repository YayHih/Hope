 <template >
  <!-- <div id="nav" > -->
  <!--  <router-link to="/" class="home" >Hope </router-link> compenents are where you put the buttons and that type of UI, rather than this being a router link it is going to be a button so when u sign in you can click on it and it will show u things -->
  <!-- <router-link to="/about">About</router-link> -->

  <!-- </div> -->
  
  <router-view />
</template>

<script>
</script>



<style>
.previous {
  font-size: 30px;
  top: 1.1rem;
  left: 1.4rem;
  position: absolute;
  margin: 0;
  padding: 10px 20px;
  background-color: #0bf0be;
  color: black;
  border-radius: 50%;
}
.maincon {
  font-family: Arial, Helvetica, sans-serif;
  position: absolute;
  color: black;
  top: 4em;
  left: 0;
  width: 100%;
  margin: 0;
  text-align: center;
}
.home {
  text-decoration: none;
  display: inline-block;
  padding: 1em 2em;
  font-weight: bold;
  background-color: #000000;
  color: white;
  border-radius: 10%;
  margin: 20px;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height: 100vh;
  width: 100vw;
}

/* #nav {
   padding: 30px; 
} */

#nav a {
  font-weight: bold;
}

#nav a.router-link-exact-active {
  color: #ffffff;
}
html {
  background-image: linear-gradient(
    to bottom right,
    rgb(30, 202, 151),
    rgb(46, 104, 192)
  );
}
body {
  margin: 0;
}
.button {
  text-decoration: none;
  display: inline-block;
  padding: 1em 2em;
  flex-direction: column;
  justify-content: space-around;
  width: min-content;
  height: 80px;
  /* font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;
		
	

		
		align-items: center;

		/* right: 1rem;
		height: 10rem;
		min-width: 100px;
		margin-top: .5rem; */

  /* width: min-content;
		height: 120px;
		padding: 2rem 1rem;
		border-radius: 12px;
background-clip: padding-box;
		margin: 4px; */

  text-decoration: none;

  background-color: #04aa6d;
  color: white;
  border-radius: 10%;
  margin: 8px;
}

.button:hover {
  background-color: #ddd;
  color: black;
  padding: 1em 2em;
}
.button img {
  width: 50px;
  height: 50px;
}
.continue {
  text-decoration: none;
  padding: 1.5em 2em;
  justify-content: space-around;
  width: min-content;
  height: 8px;

  text-decoration: none;

  background-color: #04aa6d;
  color: white;
  border-radius: 10%;
  margin: 8px;
}

.continue:hover {
  background-color: #ddd;
  color: black;
  padding: 1.5em 2em;
}
.continue  img {
  width: 50px;
  height: 50px;
  vertical-align: middle;
}
#hotlines {
  font-family: Arial, Helvetica, sans-serif;
  position: absolute;
  color: black;
  bottom: 1em;
  left: 0;
  width: 100%;
  margin: 0;
  text-align: center;
}
</style>
