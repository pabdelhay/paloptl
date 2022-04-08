function plotChart(data) {
    am4core.ready(function() {

            // Themes begin
        am4core.useTheme(am4themes_animated);
             // Themes end

        // Create chart instance
        var chart = am4core.create("chartdiv", am4charts.PieChart);

            // Add data
        chart.data = data; /*[ {
          "country": "Lithuania",
          "litres": 501.9
        }, {
          "country": "Czechia",
          "litres": 301.9
        }, {
          "country": "Ireland",
          "litres": 201.1
        }, {
          "country": "Germany",
          "litres": 165.8
        }, {
          "country": "Australia",
          "litres": 139.9
        }, {
          "country": "Austria",
          "litres": 128.3
        }, {
          "country": "UK",
          "litres": 99
        }, {
          "country": "Belgium",
          "litres": 60
        }, {
          "country": "The Netherlands",
          "litres": 50
        } ];*/

        // Add and configure Series
        var pieSeries = chart.series.push(new am4charts.PieSeries());
        //pieSeries.dataFields.value = "litres";
        pieSeries.dataFields.value = "percent";
        pieSeries.dataFields.category = "year";
        //pieSeries.dataFields.category = "country";
        pieSeries.slices.template.stroke = am4core.color("#fff");
        pieSeries.slices.template.strokeWidth = 2;
        pieSeries.slices.template.strokeOpacity = 1;

        // This creates initial animation
        pieSeries.hiddenState.properties.opacity = 1;
        pieSeries.hiddenState.properties.endAngle = -90;
        pieSeries.hiddenState.properties.startAngle = -90;

    }); // end am4core.ready()

}
function getData(id){
    //alert('Ola,mundo');
    var url = '/api/mozambique-custodio/expense/?country='+id;
    $.get(url, function(result){
        console.log(result);
        plotChart(result);

    }).fail(function (){
        console.log("Error on fatching budget basic info.")
    });
}

$(document).ready(function(){
    getData();

    $(document).on('change', '#id_country', function (ev) {
        id = $('#id_country').val();
        console.log(id)
        getData(id);

    });

});

