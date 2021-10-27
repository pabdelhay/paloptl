function budget_category_percentage(year, category , callback){
        var url = url = '/api/budgets/budget_category_percentage/?year='+year+'&category='+category;
        $.get(url, function (data) {
            callback(data);
        }).fail(function () {
            console.log("Error on fetching budget basic info.");
        });
}

function budget_category_percentage_callback(data){
    console.log(data)
    var i=0, html="";
    for(;i<data.length;i++){
        html=html+" <div>"+data[i].country+" - "+data[i].percent+"</div>";
    }
    $("#teste_country").html(html)
}

$(document).on('click', '.ano', function(ev){
    ev.preventDefault();
    var year = $(this).text();
    console.log(year)
    budget_category_percentage(year,'SAÚDE',budget_category_percentage_callback )
});