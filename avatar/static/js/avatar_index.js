var instanceUnity;
var currentPage;

$(document).ready(function()
{    
    currentPage = getCurrentPage();

    AddAvatarComponent();
    LoadAvatarContent(); 
    SetEventFunctions();
});

function tagAvatarExist()
{
    let tag = document.getElementsByTagName('avatar-container'); 
    return tag.length;
}

async function LoadAvatarContent() 
{
    $("avatar-container").load("/avatar/interface/");
}

function AddAvatarComponent()
{
    $('body').append(`
        <div class="pagina_avatar">
            <avatar-container></avatar-container>
            <div id="botoes">
                <button class="button" id="hide">Hide Avatar</button>
                <button class="button" id="show">Show Avatar</button>
            </div>
        </div>
    `);
}

function getCurrentPage()
{
    var path = location.pathname;
    if(path.length <= 1) return "home";
    else return "tutorial";
}  

function SetEventFunctions()
{
    $("#hide").click(function()
    {
        $("#hide").hide();
        $("#show").show();
        $("avatar-container").fadeOut(200);
        Hide();
        
    });

    $("#show").click(function()
    {
        $("#show").hide();
        $("#hide").show();
        $("avatar-container").fadeIn(200);
        Show(); 
    });

    // start tutorial
    $(document).on('click', '.tutorial', function(ev){
        ev.preventDefault();
        StartTutorial();
    });
    
    // exit tutorial
    $(document).on('click', '.introjs-overlay', function(ev){
        ev.preventDefault();
        CancelTutorial();
        console.log("sxit tutorial");
    });
    
    // exit tutorial
    $(document).on('click', '.introjs-skipbutton', function(ev){
        ev.preventDefault();
        console.log("skip tutorial");
        CancelTutorial();
    });

    // next tutorial 
    $(document).on('click', '.introjs-nextbutton', function(ev){
        ev.preventDefault();
        NextTutorial();
    });
    // previous tutorial 
    $(document).on('click', '.introjs-prevbutton', function(ev){
        ev.preventDefault();
        PreviousTutorial();
    });
}