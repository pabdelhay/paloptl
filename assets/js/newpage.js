//BINDS
$(document).ready(function(){
    $(".year").click(function()
    {
        budget_category_percentage($(this).text());
    });
});

//FUNCTIONS
function budget_category_percentage(year)
{
    var url = '/api/budgets/budget_category_percentage/?category=saúde&year=' + year;
    console.log("url: " + url);
    $.get(url, function (data)
    {
        console.log(data);
        $('#list_countries').empty();
        for (var d in data)
        {
            var country = data[d];
            console.log(country);
            var p = country['percental'];
            p = p.toFixed(2);
            console.log("vvv" + p);
            var country_percent = country['country'] + " - " + (p * 100) + "%";
            $('#list_countries').append('<p>' + country_percent + '</p>')

        }
    }).fail(function () {
        console.log("Error on fetching budget basic info.");
    });
}

function get_budget_category_percentage()
{
    var url = '/api/budgets/budget_category_percentage/?category=saúde&year=2019';
    $.get(url, function (data)
    {
        var list = [];

        for (var d in data)
        {
            var country = data[d];
            var country_percent = country['country'] + " - " + (country['percental'].toFixed(2) * 100) + "%";
            var dic = {
                "couttry":country['country'],
                "percental" : country['percental']
                };
            //$('#list_countries').append('<p>' + country_percent + '</p>')
            list.push(dic);
            console.log(dic);
        }
        //console.log("dd " + list);
        return data;
    }).fail(function () {
        console.log("Error on fetching budget basic info.");
    });
}

