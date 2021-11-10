function getExpensesRevenuesAPI() {
    let url = "/api/budgets/expenses_and_revenues/?country=" +$(".country").attr("country_id");
    $.get(url, function (result) {
        plotChart(result);
    }).fail(function () {
        console.log("Error on fetching expenses and revenues.");
    });
}


function plotChart(data){
    am4core.useTheme(am4themes_animated);

// Themes end

// Create chart instance
var chart = am4core.create("chartdiv", am4charts.XYChart);
chart.data = data;
chart.colors.list = [
  am4core.color("#0F69A3"),
  am4core.color("#98B8DA"),
  am4core.color("#C90000"),
  am4core.color("#FF8080")
];

// Create axes
var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
categoryAxis.dataFields.category = "year";
categoryAxis.renderer.grid.template.location = 0;
categoryAxis.renderer.minGridDistance = 20;
categoryAxis.renderer.cellStartLocation = 0.2;
categoryAxis.renderer.cellEndLocation = 0.8;
categoryAxis.numberFormatter = new am4core.NumberFormatter();
categoryAxis.numberFormatter.numberFormat = "###";
categoryAxis.renderer.grid.template.disabled = true;

var  valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
valueAxis.min = 0;
valueAxis.numberFormatter = new am4core.NumberFormatter();
valueAxis.numberFormatter.numberFormat = "#,###.00";
valueAxis.renderer.grid.template.disabled = true;
//valueAxis.title.text = "Expenditure (M)";

// Create series
function createSeries(field, name, width, dx) {
  var series = chart.series.push(new am4charts.ColumnSeries());
  series.dataFields.valueY = field;
  series.dataFields.categoryX = "year";
  series.name = name;
  console.log(name);
  if(name.toLowerCase().includes("despesa")){
     series.columns.template.tooltipText = `[bold]{year}[/]   [bold]{valueY}[/]   ${name} de acordo com grupamento {expense_group}`;
  }
  else{
        series.columns.template.tooltipText = `[bold]{year}[/]  [bold]{valueY}[/] ${name} de acordo com grupamento {revenue_group}`;
  }
  //series.columns.template.tooltipText = "{name}: [bold]{valueY}[/]";
  series.clustered = false;
  series.dx = dx;
  series.columns.template.width = width;
}

createSeries("execution_revenue", "Execução Despesa", 60, -40);
createSeries("budget_revenue", "Dotação Despesa", 40, -40);
createSeries("execution_expense", "Execução Receita", 60, 40);
createSeries("budget_expense", "Dotação Receita", 40, 40);
}

getExpensesRevenuesAPI();