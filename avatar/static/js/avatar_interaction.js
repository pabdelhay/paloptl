
class AvatarConfig 
{
  // buildUrl = "/static/Build";
  loaderUrl = avatar_loader_url;
  config = {};
  avatarInstance;
  
  constructor() {
    this.config = {
      dataUrl: avatar_data_url,
      frameworkUrl: avatar_framework_url,
      codeUrl: avatar_code_url,
      streamingAssetsUrl: "StreamingAssets",
      companyName: "Bonako",
      productName: "Ready Player Me WebGL",
      productVersion: "0.1"
    };
  }

  getConfig() {
    return this.config;
  }
  
  getLoaderUrl() {
    return this.loaderUrl;
  }
  getInstance() {
    return this.avatarInstance;
  }

  callInstance(canvas) {
    var script = document.createElement("script");
    script.src = this.loaderUrl;
    console.log(this.loaderUrl);
    document.body.appendChild(script);

    return new Promise((resolve, reject) => {
      script.onload = () => {
        createUnityInstance(canvas, this.config).then((instance) => {
          this.avatarInstance = instance;
          ShowButtons();
          startInteraction();
          resolve();
        }).catch((error) => {
          reject(error);
        });
      };
    });
  }
}


var tutorialcount = 0;
var avatarInstance = false; // instancia global do avatarInstance

var statusAvatar = false;

var canvas = document.querySelector("#unity-canvas");

// definir em css 
canvas.style.width = "250px";
canvas.style.height = "350px";

var avatarConfig = new AvatarConfig();

avatarConfig.callInstance(canvas).then(() => 
{
  console.log("instance created successfully.");
  avatarInstance = avatarConfig.getInstance();
}).catch((error) => 
{
  console.log("Error creating instance:", error);
});

function isFirstTime() 
{
  if (localStorage.getItem("first_time_avatar") === null) 
  {
    localStorage.setItem("first_time_avatar", "1");
    return true;
  } 
  else
  {
    return false;
  }  
}

var tempStart = 3500;

function startInteraction() 
{
  console.log("startInteraction");
  
  setTimeout(() => {
    var first = isFirstTime();
    var interaction = "";
    
    if(first) interaction = currentPage;
    else interaction = getOptionInteraction();

    checkOptionChoose(interaction);
    ShowAvatar();
    tempStart = 10;
  }, tempStart); 

}

function SendAction(action)
{
  avatarInstance.SendMessage('JavascriptHook','SetActionAvatar', action);
}

function getOptionInteraction()
{
  var option = getInteractionOptionAndClear();
  return option;
}

function getInteractionOptionAndClear() 
{
  var option = localStorage.getItem("action_avatar");
  localStorage.setItem("action_avatar","");
  return option;
}

function checkOptionChoose(option) 
{
  switch (option) 
  {
    case "home":
      SendAction("home");
      break;
    case "tutorial":
      SendAction("tutorial");
      break;
    case "indice":
      goIndice();
      break;
    case "country":
      goTutorial();
      break;
    default:
      console.log("default: " + currentPage);
      SendAction("default_" + currentPage);
      break;
  }
}

// HOME
// in home, go to indice component and play 
function goIndice() 
{
  document.querySelector(".ranking-header").scrollIntoView({
    behavior: 'smooth'
  });
  
  setTimeout(() => {
    ShowAvatar();
    SendAction("indice");
  }, 500);
}

// open list country
function goCountry() 
{
  document.querySelector(".header").scrollIntoView({
    behavior: 'smooth'
  });
  
  setTimeout(() => {
    ShowAvatar();
    SendAction("country");
    localStorage.setItem("action_avatar", "country");
  }, 500);
}

// TUTORIAL
function goIndiceHome() 
{
  localStorage.setItem("action_avatar", "indice");
  window.location.href = "/";
}

function goTutorial() 
{
  document.querySelector(".header").scrollIntoView({
    behavior: 'smooth'
  });
  
  setTimeout(() => {
    ShowAvatar();
    StartTutorial();
    start_tutorial(); // tutorial from side
  }, 500);
}

function goCountryTutorial() 
{
  document.querySelector(".header").scrollIntoView({
    behavior: 'smooth'
  });
  
  setTimeout(() => {
    document.querySelector(".dropdown-content").style.display = "block";
    avatarInstance.SendMessage('JavascriptHook','SetActionAvatar', "country");
  }, 500);
  countryStatus = true;
  localStorage.setItem("country", true);
  //verifyCountryClick();
}

function ShowButtons()
{
  $("#botoes").show();
  $("#hide").show();
  $("#show").hide();
}

function StartTutorial()
{  
  console.log("start tutorial func");
  tutorialcount = 0;

  let count = 0;

  let iWaitInstance = setInterval(() => {
    count++;

    if(avatarInstance !== null)

    {
      avatarInstance.SendMessage('JavascriptHook','PlayTutorial', 0);
      waitForAvatar();
      clearInterval(iWaitInstance);
    }
    
    if(count >= 20) clearInterval(iWaitInstance);

  }, 200);
}

function waitForAvatar()
{
  var iWaitAvatar = setInterval(() => {
    if(statusAvatar) 
    {
      ShowAvatar();
      clearInterval(iWaitAvatar);
    }
  }, 100);  
}

function CancelTutorial()
{
  console.log("cancel tutorial");
  SendAction("stop_tutorial");
}

function ShowAvatar()
{
  setAvatarPosition();
  $(".pagina_avatar").show();
}

function setAvatarPosition()
{
  var left = "75%";
  var right = "10%";

  switch (tutorialcount) 
  {
    case 7:
      $(".pagina_avatar").css("right",right);
      break;
    case 8:
      $(".pagina_avatar").css("right",right);
      break;
    case 10:
      $(".pagina_avatar").css("right",right);
      break;
    case 11:
      $(".pagina_avatar").css("right",right);
      break;
    default:
      $(".pagina_avatar").css("right",left);
      break;
  }
}

function PreviousTutorial()
{
  tutorialcount--;
  console.log("tuto previous: " + tutorialcount);
  setAvatarPosition();
  avatarInstance.SendMessage('JavascriptHook','PreviousTutorial');
}

function NextTutorial()
{
  tutorialcount++;
  console.log("tuto next: " + tutorialcount);
  setAvatarPosition();
  avatarInstance.SendMessage('JavascriptHook','NextTutorial');
}

// SHOW AND RIDE AVATAR FUNCTION
function Hide() 
{
  getInteractionOptionAndClear();
  SendAction("hide_avatar");  
}

function Show() 
{
  avatarInstance.SendMessage('JavascriptHook','Show');
}