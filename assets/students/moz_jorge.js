





<!-- Chart code -->
function chartList(result   ){
  am4core.ready(function() {

// Themes begin
am4core.useTheme(am4themes_animated);
// Themes end

// Create chart instance
var chart = am4core.create("chartdiv", am4charts.PieChart);

// Add data
chart.data = result

// Add and configure Series
var pieSeries = chart.series.push(new am4charts.PieSeries());
pieSeries.dataFields.value = "percent";
pieSeries.numberFormatter = new am4core.NumberFormatter();
pieSeries.numberFormatter.numberFormat = "#";
pieSeries.dataFields.category = "year";
pieSeries.slices.template.stroke = am4core.color("#fff");
pieSeries.slices.template.strokeOpacity = 1;

// This creates initial animation
pieSeries.hiddenState.properties.opacity = 1;
pieSeries.hiddenState.properties.endAngle = -90;
pieSeries.hiddenState.properties.startAngle = -90;

chart.hiddenState.properties.radius = am4core.percent(0);


}); // end am4core.ready()
};

function changeTitulo(result){
  document.getElementById("country").innerHTML = result[1].country;
}
function getData(years){
    var url = '/api/mozambique-jorge/myapi/?country='+years;
    $.get(url, function(result){
        console.log(result);
        console.log(result[1].country);
        changeTitulo(result);
        chartList(result);
    }).fail(function (){
        console.log('error')
    });
}

$(document).ready(function(){
    getData()
    $(document).on('change','#id_years', function(ev){
      alert("salkd");
      years = $("#id_years").val();
      console.log(years);
      getData(years);
    })

});
