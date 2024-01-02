<template>
  <div class="Home">  
    <div class="button-holder">
      <div id="app">
  <header class="header">
    <nav class="header__nav">
      <ul class="header__navbar">
        <li class="header__item">
          <a href="#" class="header__link">
            <transition name="slide-fade">
              <!-- Header Navigation Menu Icons -->
              <button class="header--button" v-if="show" key="on" @click="show = false">
                <svg viewBox="0 0 24 24" class="header--icon">
                  <title>Close</title>
                  <path d="M0 0h24v24H0V0z" fill="none" />
                  <path fill="currentColor" d="M18.3 5.71c-.39-.39-1.02-.39-1.41 0L12 10.59 7.11 5.7c-.39-.39-1.02-.39-1.41 0-.39.39-.39 1.02 0 1.41L10.59 12 5.7 16.89c-.39.39-.39 1.02 0 1.41.39.39 1.02.39 1.41 0L12 13.41l4.89 4.89c.39.39 1.02.39 1.41 0 .39-.39.39-1.02 0-1.41L13.41 12l4.89-4.89c.38-.38.38-1.02 0-1.4z" />
                </svg>
              </button>
              <button class="header--button" v-else key="off" @click="show = true">
                <svg viewBox="0 0 24 24" class="header--icon">
                  <title>Navigation Menu</title>
                  <path fill="currentColor" d="M6,8c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2zM12,20c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2zM6,20c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2zM6,14c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2zM12,14c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2zM16,6c0,1.1 0.9,2 2,2s2,-0.9 2,-2 -0.9,-2 -2,-2 -2,0.9 -2,2zM12,8c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2zM18,14c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2zM18,20c1.1,0 2,-0.9 2,-2s-0.9,-2 -2,-2 -2,0.9 -2,2 0.9,2 2,2z" />
                </svg>
              </button>
            </transition>
          </a>
          <!-- Dropdown Menu -->
          <transition name="dropdown">
            <div class="dropdown__menu" v-bind:class="{ active: show }" v-if="show">
              <ul class="dropdown__menu-nav">
                
                <li class="dropdown__menu-item">
                  <a href="/personal_info" class="dropdown__menu-link" title="Personal info">
					  
                    <div class="dropdown__menu-svg">
                      <svg viewBox="0 0 576 512">
                        <path fill="currentColor" d="M512 32H64C28.7 32 0 60.7 0 96v320c0 35.3 28.7 64 64 64h448c35.3 0 64-28.7 64-64V96c0-35.3-28.7-64-64-64zm32 384c0 17.6-14.4 32-32 32H64c-17.6 0-32-14.4-32-32V96c0-17.6 14.4-32 32-32h448c17.6 0 32 14.4 32 32v320zm-72-128H360c-4.4 0-8 3.6-8 8v16c0 4.4 3.6 8 8 8h112c4.4 0 8-3.6 8-8v-16c0-4.4-3.6-8-8-8zm0-64H360c-4.4 0-8 3.6-8 8v16c0 4.4 3.6 8 8 8h112c4.4 0 8-3.6 8-8v-16c0-4.4-3.6-8-8-8zm0-64H360c-4.4 0-8 3.6-8 8v16c0 4.4 3.6 8 8 8h112c4.4 0 8-3.6 8-8v-16c0-4.4-3.6-8-8-8zM208 288c44.2 0 80-35.8 80-80s-35.8-80-80-80-80 35.8-80 80 35.8 80 80 80zm0-128c26.5 0 48 21.5 48 48s-21.5 48-48 48-48-21.5-48-48 21.5-48 48-48zm46.8 144c-19.5 0-24.4 7-46.8 7s-27.3-7-46.8-7c-21.2 0-41.8 9.4-53.8 27.4C100.2 342.1 96 355 96 368.9V392c0 4.4 3.6 8 8 8h16c4.4 0 8-3.6 8-8v-23.1c0-7 2.1-13.8 6-19.6 5.6-8.3 15.8-13.2 27.3-13.2 12.4 0 20.8 7 46.8 7 25.9 0 34.3-7 46.8-7 11.5 0 21.7 5 27.3 13.2 3.9 5.8 6 12.6 6 19.6V392c0 4.4 3.6 8 8 8h16c4.4 0 8-3.6 8-8v-23.1c0-13.9-4.2-26.8-11.4-37.5-12.3-18-32.9-27.4-54-27.4z" />
                      </svg>
                    </div>
                    <div class="dropdown__menu-text">Personal info</div>
					
					<!-- perhaps change personal info to "what we collect" or something like that -->
                  </a>
                </li>
                <!-- for this part, just tell them the cookies that we collect and a way to reset the cookies/ change them -->
                
                <!-- Dropdown Menu Separator -->
                <li class="dropdown__menu-item">
                  <a href="/help" class="dropdown__menu-link" title="Send feedback">
                    <div class="dropdown__menu-svg">
                      <svg viewBox="0 0 512 512">
                        <path fill="currentColor" d="M448 0H64C28.7 0 0 28.7 0 64v288c0 35.3 28.7 64 64 64h96v84c0 7.1 5.8 12 12 12 2.4 0 4.9-.7 7.1-2.4L304 416h144c35.3 0 64-28.7 64-64V64c0-35.3-28.7-64-64-64zm32 352c0 17.6-14.4 32-32 32H293.3l-8.5 6.4L192 460v-76H64c-17.6 0-32-14.4-32-32V64c0-17.6 14.4-32 32-32h384c17.6 0 32 14.4 32 32v288zm-224-88c-13.3 0-24 10.7-24 24s10.7 24 24 24 24-10.7 24-24-10.7-24-24-24zm-8.5-24h17c4.2 0 7.7-3.3 8-7.5l7-112c.3-4.6-3.4-8.5-8-8.5h-31c-4.6 0-8.3 3.9-8 8.5l7 112c.3 4.2 3.8 7.5 8 7.5z" />
                      </svg>
                    </div>
                    <div class="dropdown__menu-text">Help</div>
                  </a>
                </li>
                <li class="dropdown__menu-item">
                  <a href="/about" class="dropdown__menu-link" title="Help">
                    <div class="dropdown__menu-svg">
                      <svg viewBox="0 0 512 512">
                        <path fill="currentColor" d="M256 340c-15.464 0-28 12.536-28 28s12.536 28 28 28 28-12.536 28-28-12.536-28-28-28zm7.67-24h-16c-6.627 0-12-5.373-12-12v-.381c0-70.343 77.44-63.619 77.44-107.408 0-20.016-17.761-40.211-57.44-40.211-29.144 0-44.265 9.649-59.211 28.692-3.908 4.98-11.054 5.995-16.248 2.376l-13.134-9.15c-5.625-3.919-6.86-11.771-2.645-17.177C185.658 133.514 210.842 116 255.67 116c52.32 0 97.44 29.751 97.44 80.211 0 67.414-77.44 63.849-77.44 107.408V304c0 6.627-5.373 12-12 12zM256 40c118.621 0 216 96.075 216 216 0 119.291-96.61 216-216 216-119.244 0-216-96.562-216-216 0-119.203 96.602-216 216-216m0-32C119.043 8 8 119.083 8 256c0 136.997 111.043 248 248 248s248-111.003 248-248C504 119.083 392.957 8 256 8z" />
                      </svg>
                    </div>
                    <div class="dropdown__menu-text">About</div>
                  </a>
                </li>
              </ul>
            </div>
          </transition>
        </li>
      </ul>
    </nav>
    
  </header>
  <div class="buttons">
	<div class="links">
		<router-link class="middle-buttons" to="/volenteering"><img src="volenteer_icon.png"/>Volenteering</router-link>
		<router-link class="middle-buttons" to="/Shelters"><img src="shelter.png"/>Shelters</router-link>
		<router-link class="middle-buttons" to="/Soupkitchens"><img src="soup_kitchen.png"/>Soupkitchens</router-link>
		<router-link class="middle-buttons" to="/Link_nyc"><img src="link_nyc.png"/>Link NYC</router-link>
	</div>
	<router-link class="mapping-button" to="/mapping"><img src="default_map.png"/>Mapping</router-link>
  </div>
</div>
<!-- chirisits hotlines 741 741 suciude hotline ammi religous hotlines https://www.brc.org/ -->
    
    </div>
    
  </div>
  <p id="hotlines">
    Note: If you are experiencing an emergency, please dial
    <a href="tel:911">911</a> or the relevant
    <a href="http://localhost:8080/Hotlines">hotline</a>.
  </p>
</template>

<script>
export default {
  name: "Home",
  data: function() {
    return {
      show: false
    }
  },
  methods: {
  }
};
</script>
<style scoped>
:root {
	 --font-primary: 'Open Sans', sans-serif;
	 --color-gray: #dadce0;

}
 *, ::after, ::before {
	 box-sizing: border-box;
}
 body {
	 font-size: 1rem;
	 -webkit-text-size-adjust: 100%;
	 /* font-family: var(--font-primary); */
	 font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;
	 overflow: hidden;
}
 hr {
	 border: 0;
	 height: 0;
	 margin: 1.5rem 0;
	 border-top: 1px solid var(--color-gray);
}
 .header {
	 padding: 1rem 1rem 1rem 1rem;
}
 .header__nav {
	 position: relative;
}
 .header__navbar {
	 display: flex;
	 align-items: center;
	 justify-content: flex-end;
}
 .header__item {
	 padding: 1rem;
	 list-style-type: none;

}
 .header--icon {
	 width: 3rem;
	 height: 3rem;
}
 .header--button {
	 top: 0;
	 left: 0;
	 position: absolute;
	 margin: 0;
	 padding: 0;
	 color: rgb(65, 64, 64);
	 cursor: pointer;
	 border: 1px solid transparent;
	 background-color: transparent;
}
 .header--button:focus {
	 outline: 0;
}
 .dropdown__menu {
   backdrop-filter: blur(5px);
	 top: 100%;
	 left: 0;
	 position: absolute;
	 z-index: 10;
	 height: 12rem;
	 min-width: 300px;
	 margin-top: 1rem;
	 padding: 1rem 1rem 1rem 0rem;
	 border-radius: 12px;
	 background-color: white;
	 border: 1px solid var(--color-gray);
	 background-clip: padding-box;
}
 .dropdown__menu-link {
	 display: flex;
	 align-items: center;
	 justify-content: flex-start;
	 text-decoration: none;
	 color: rgba(0, 0, 0, 0.6);
	 padding: 0.8rem 0 0.8rem 2rem;
	 margin-top: 0.3rem;
	 margin-bottom: 0.2rem;
	 border-radius: 0 50px 50px 0;
}
 .dropdown__menu-link:hover {
	 color: #17bf63;
	 background-color: rgba(79, 192, 141, 0.1);
}
 .dropdown__menu-svg {
	 width: 1.5rem;
	 height: 1.5rem;
}
 .dropdown__menu-text {
	 font-weight: 300;
	 margin-left: 1rem;
	 margin-right: 1rem;
}
 .slide-fade-enter-active, .slide-fade-leave-active {
	 transition: all 0.3s;
}
 .slide-fade-enter, .slide-fade-leave-active {
	 opacity: 0;
}
 .slide-fade-enter {
	 transform: translateX(31px);
}
 .slide-fade-leave-active {
	 transform: translateX(-31px);
}
 .dropdown-enter-active, .dropdown-leave-active {
	 transition: all .3s;
}
 .dropdown-enter, .dropdown-leave-to {
	 opacity: 0;
	 transform: translateY(30px);
}
 .main {
	 margin: 6rem;
	 display: flex;
	 flex-wrap: wrap;
	 align-items: center;
	 justify-content: center;
	 flex-direction: column;
}
 .main__subtitle {
	 color: #4f5959;
	 font-weight: 100;
	 margin-bottom: 2rem;
}
 .main__link {
	 margin-right: 1.5rem;
	 display: inline-block;
}
 .main__link:last-child {
	 margin-right: 0;
}
 .main__svg {
	 width: 2rem;
	 height: 2rem;
	 opacity: 0.6;
	 color: #94a2b0;
}
 .main__svg:hover {
	 color: #ffad1f;
}

</style>
<!-- https://vuejsexamples.com/animated-dropdown-menu-with-vue-js/ ^above is options style -->
<style scoped>

	.links {
		display: flex;
		flex-direction: row;

		justify-content: center; 
		flex-wrap: wrap;

		width: 100%;
		
	}
	.buttons {
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.mapping-button{
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		align-self: center;
		flex-wrap: wrap;
		width: min-content;
		/* height: 33px; */
		padding: 1rem 1rem;
		border-radius: 12px;
		background: rgb(241, 241, 241);
		background-clip: padding-box;
		/* margin: 4px; */

		text-decoration: none;
		color: black;	
	}
	.mapping-button img {
		border-radius: 7px;
	}
	.middle-buttons {
		font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif;
		display: flex;
		flex-direction: column;

		justify-content: space-around;
		align-items: center;

		/* right: 1rem;
		height: 10rem;
		min-width: 100px;
		margin-top: .5rem; */

		width: min-content;
		height: 120px;
		padding: 2rem 1rem;
		border-radius: 12px;
		border: 1.75px solid gray;
		background: rgb(241, 241, 241);
		background-clip: padding-box;
		margin: 4px;

		text-decoration: none;
		color: black;
	}
	.middle-buttons img {
		width: 75px;
		height: 75px;
	}
</style>