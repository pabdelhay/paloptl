var avatar;

$(document).ready(async function() {
  avatar = new AvatarView();
  avatar.start(); 
});

/*  classe avatar view */
class AvatarView 
{
  routeContainer = "/avatar/container/";
  routeView = "/avatar/interface/";

  constructor() {
    this.loading = $("#loading");
    this.loading.hide();
  }
  
  async start()
  {
    this.loading.show();
    this.getContainer().then(() => this.getAvatar());
  }

  async getContainer() {
    try {
      await $.get(this.routeContainer, (data) => {
        $("body").append(data);
        this.avatarContainer = $("avatar-container");
        this.avatarContainer.hide();
      });
      return Promise.resolve();
    } catch (error) {
      return Promise.reject(error);
    }
  }
  
  async getAvatar() {
    try {
      const data = await $.ajax({url: this.routeView});
      await $(this.avatarContainer).html(data).promise();
      this.loadSucess();
      return Promise.resolve();
    } catch (error) {
      return Promise.reject(error);
    }
  }

  loadSucess()
  {
    this.setEventActions();
    const orientation = new AvatarOrientation();
    orientation.init();
  }

  ShowAvatar()
  {
    $(this.loading).hide();
    this.avatarContainer.show();
    this.DisplayAvatarButtons(true);
  }

  DisplayAvatarButtons(value) {
    this.hide.toggle(value);
    this.show.toggle(!value);
    $("#botoes").show();
  }

  setEventActions()
  {
    this.setHideEvents();
    this.setShowEvents();
  }
  
  setHideEvents() {
    this.hide = $("#hide");  
    this.hide.hover(() => $(".texto-oculto").show(), () => $(".texto-oculto").hide());
    
    this.hide.click(() => {
      this.hide.hide();
      this.show.show();
      $(this.avatarContainer).fadeOut(200);
      avatarConfig.Hide();
    });
  }

  setShowEvents() {
    this.show = $("#show");  
    this.show.hover(() => $(".texto-oculto").show(), () => $(".texto-oculto").hide());
    
    this.show.click(() => {
      avatarConfig.Show(); 
      this.ShowAvatar();
      this.hide.show();
      this.show.hide();
    });
  }
}

/* class orientation for move avatar on the screen */
class AvatarOrientation {
    constructor() {
      this.currentOrientation = "left";
      this.avatarPage = $(".pagina_avatar");    
      this.avatarView = $("#avatar-views");  
      this.buttonsActionAvatar = $("#botoes");
      this.txtInfoButton = $('.texto-oculto');
      this.imgButton = $(".imagem-centralizada");
    }
    
    init()
    {
      this.setEventNavegation();
      this.orientationLeft();
    }

    setEventNavegation()
    {
        $("#move_left").on("click", () => this.moveAvatar("left"));
        $("#move_right").on("click", () => this.moveAvatar("right"));

        $(this.avatarView).on('mouseenter', () => {
            $("#move_container").stop().slideToggle(200);
        });
        
        $(this.avatarView).on('mouseleave', () => {
            $("#move_container").stop().slideToggle(200);
        });
    }
  
    orientationLeft() {
      this.avatarPage.css('right', "auto");
      this.buttonsActionAvatar.css({left: "100%", right: "auto"});
      this.imgButton.css('order', "1");
      this.txtInfoButton.css('order', "2");
      $("#move_left").hide();
      $("#move_right").show();
    }
  
    orientationCenter() {
      this.avatarPage.css('right', "50%");
      this.buttonsActionAvatar.css({left: "100%", right: "auto"});
      this.imgButton.css('order', "1");
      this.txtInfoButton.css('order', "2");
      $("#move_left, #move_right").show();
    }
  
    orientationRight() {
      this.avatarPage.css('right', "0%");
      this.buttonsActionAvatar.css({left: "auto", right: "100%"});
      this.imgButton.css('order', "2");
      this.txtInfoButton.css('order', "1");
      $("#move_right").hide();
      $("#move_left").show();
    }
  
    setDiretion(direction) {
      if (direction === "left")
        this.currentOrientation = (this.currentOrientation === "right") ? "center" : "left";
      else if (direction === "right")
        this.currentOrientation = (this.currentOrientation === "left") ? "center" : "right";
    }
  
    setNewDirection() {
      if (this.currentOrientation === "left") {
        this.orientationLeft();
      } else if (this.currentOrientation === "center") {
        this.orientationCenter();
      } else if (this.currentOrientation === "right") {
        this.orientationRight();
      }
    }
  
    moveAvatar(direction) 
    {
      this.setDiretion(direction);
      this.avatarPage.fadeOut(120);
      setTimeout(() => {
        this.setNewDirection();
        this.avatarPage.fadeIn(120);
      }, 250);
    }
  }



