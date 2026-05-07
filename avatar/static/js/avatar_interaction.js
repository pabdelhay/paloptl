
// global vars
var tutorial;
var avatarConfig;

$(document).ready(async function() {
  init();
});

// auxiliar functions

function init() 
{ 
  const canvas = document.querySelector("#unity-canvas");

  avatarConfig = new AvatarConfig();
  avatarConfig.callInstance(canvas).then(() => {
    if(avatarConfig.getCurrentPage() == "tutorial") tutorial = new Tutorial();
  }).catch((error) => 
  {
    console.log("Error loading avatar");
  });
}

function webglContentReady(params) 
{
  setTimeout(() => {
    avatarConfig.avatarReady = true;
    $("#loading").hide();
    startInteraction();
  }, 1000);
}

function startInteraction() 
{
  if(LocalStorageHandler.read("first_time_avatar") == null) 
    firstTimeAvatar();
  else 
    checkAvatarOption();
}

function firstTimeAvatar()
{
  $("#texto-mostrar").show();
  avatar.DisplayAvatarButtons(false);
  avatarConfig.resetState();
}

function checkAvatarOption() 
{
  var status = LocalStorageHandler.read("avatarStatus");
  var option = LocalStorageHandler.read("action_avatar");
  
  if (status == true && option != null) 
  {
    LocalStorageHandler.save("action_avatar", "");
    avatarConfig.checkOptionChoose(option);
    avatar.ShowAvatar();
  } 
  else 
  {
    avatar.DisplayAvatarButtons(false);
    avatarConfig.Hide();
  }
}

// functions actions navegations

//  for home page
function goIndice() 
{
  moveTo('.ranking-header');
  avatarConfig.SendAction("indice");
}

function goCountry() 
{
  moveTo('.header');
  avatarConfig.SendAction("country");
  LocalStorageHandler.save("action_avatar", "country");
}
//  for tutorial page 
function goIndiceHome() 
{
  LocalStorageHandler.save("action_avatar", "indice");
  window.location.href = "/";
}

function goTutorial() 
{
  moveTo(".header");
  tutorial.start();
  start_tutorial();
}

function goCountryTutorial() 
{
  moveTo(".header");
  $(".dropdown-content").show();
  avatarConfig.SendAction("country");
  LocalStorageHandler.save("country", true);
  setTimeout(() => {
    $(".dropdown-content").hide();
  }, 5000);
}

function moveTo(target)
{
  $(target).get(0).scrollIntoView({ behavior: 'smooth' });
}

// classes
class AvatarConfig 
{
  loaderUrl = avatar_loader_url;
  config = {};
  avatarInstance = false;
  avatarReady = false;
  
  constructor() {
    this.config = {
      dataUrl: avatar_data_url,
      frameworkUrl: avatar_framework_url,
      codeUrl: avatar_code_url,
      streamingAssetsUrl: "StreamingAssets",
      companyName: "Bonako sa",
      productName: "Avatar Assistent",
      productVersion: "0.2",
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
  isAvatar()
  {
    return this.avatarReady;
  }

  callInstance(canvas) {
    var script = document.createElement("script");
    script.src = this.loaderUrl;
    document.body.appendChild(script);
    
    return new Promise((resolve, reject) => {
      script.onload = () => {
        createUnityInstance(canvas, this.config).then((instance) => {
          this.avatarInstance = instance;
          this.start();
          resolve();
        }).catch((error) => {
          reject(error);
        });
      };
    });
  }

  start()
  {
    LocalStorageHandler.save("intutorial",false);
    this.setWindowsEvent();
  }

  Hide() 
  {
    this.SendAction("hide_avatar");  
    LocalStorageHandler.save("action_avatar","");
    LocalStorageHandler.save("avatarStatus",false);
  }

  Show() 
  {
    LocalStorageHandler.save("avatarStatus",true);
    var avatarExist = LocalStorageHandler.read("first_time_avatar");
    var tutorial = LocalStorageHandler.read("intutorial");

    if(avatarExist == null && tutorial == false)
    {
      LocalStorageHandler.save("first_time_avatar",true);
      this.SendActionOption("AvatarState",1);
      this.SendAction(this.getCurrentPage());
    }
    else 
    {
      avatarConfig.SendAction("show_avatar");
    }
  }

  resetState() {
    this.SendActionOption("AvatarState", 0);
    LocalStorageHandler.save("action_avatar", "");
  }

  // actions
  SendAction(action)
  {
    if(this.isAvatar())
      this.avatarInstance.SendMessage('JavascriptHook','SetActionAvatar', action);
  }
  
  SendActionOption(option)
  {
    if(this.isAvatar())
      this.avatarInstance.SendMessage('JavascriptHook',option);
  }
  
  SendActionOption(option, action)
  {
    if(this.isAvatar())
      this.avatarInstance.SendMessage('JavascriptHook',option, action);
  }

  checkOptionChoose(option) 
  {
    const currentPage = this.getCurrentPage();
    if(currentPage == "home" && option == "country") option = "";
  
    switch (option) 
    {
      case "home":
        avatarConfig.SendAction("home");
        break;
        case "tutorial":
          avatarConfig.SendAction("tutorial");
          break;
          case "indice":
        goIndice();
        break;
        case "country":
        goTutorial();
        break;
        default:
        avatarConfig.SendAction("default_" + currentPage);
        break;
    }

  }
  ActionDefault()
  {
    this.checkOptionChoose("")
  }

  setWindowsEvent()
  {
    var self = this;
    $(window).on('blur', function() { self.SendActionOption("PauseContent"); });
    $(window).on('focus', function() { self.SendActionOption("PlayContent"); });
  }

  getCurrentPage()
  {
    var path = location.pathname;
    if(path.length <= 1) return "home";
    else return "tutorial";
  }  
}

class LocalStorageHandler 
{
  static save(key, value) {
    localStorage.setItem(key, value);
  }

  static read(key) {
    const value = localStorage.getItem(key);
    if (value === null) return null;
    if (/^-?\d+\.?\d*$/.test(value)) return Number(value);
    if (value === 'true') return true;
    if (value === 'false') return false;
    return value;
  }
}

class Tutorial {
  constructor() {
    this.tutorialcount = 0;
    this.tutorialLimit = 12;
    this.statusAvatar = false;
    this.iWaitAvatar = null;
    this.avatar = null;
    this.avatarConfig = null;
    this.LocalStorageHandler = null;

    this.setEvents();
  }

  start() {
    this.resetState();
    this.saveLocalStorage();
    this.waitForAvatar();
  }

  resetState() {
    this.tutorialcount = 0;
  }
  
  saveLocalStorage() {
    LocalStorageHandler.save("intutorial", true);
    LocalStorageHandler.save("action_avatar", "tutorial");
    LocalStorageHandler.save("first_time_avatar", true);
  }

  waitForAvatar() {
    const thisT = this;
    function checkAvatarLoaded() {
      if (avatarConfig.isAvatar() == true) {
        avatarConfig.SendActionOption("PlayTutorial", thisT.tutorialcount);
        return;
      }
      requestAnimationFrame(checkAvatarLoaded);
    }
    checkAvatarLoaded();
  }
  

  cancel() {
    avatarConfig.SendAction("stop_tutorial");
    LocalStorageHandler.save("intutorial", false);
    LocalStorageHandler.save("action_avatar", "");
  }

  previous() {
    this.tutorialcount--;
    avatarConfig.SendActionOption("PreviousTutorial");
  }

  next() 
  {
    if (this.tutorialcount >= this.tutorialLimit) {
      LocalStorageHandler.save("intutorial", false);
      avatarConfig.ActionDefault();
      return;
    } 

    this.tutorialcount++;
    if (avatarConfig.isAvatar()) {
      avatarConfig.SendActionOption("NextTutorial");
    }
  }

  setEvents()
  {
    $('.tutorial').click(function(ev) {
      ev.preventDefault();
      tutorial.start();
    });
    
    $(document).on('click', '.introjs-overlay, .introjs-skipbutton', function(ev) {
      ev.preventDefault();
      tutorial.cancel();
    });
    
    $(document).on('click', '.introjs-nextbutton', function(ev) {
      ev.preventDefault();
      tutorial.next();
    });
    
    $(document).on('click', '.introjs-prevbutton', function(ev) {
      ev.preventDefault();
      tutorial.previous();
    });
  }
}