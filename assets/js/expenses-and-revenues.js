var url = `/api/budgets/expenses_revenue_year_by_country/?country=${country.id}`;

am4core.ready(async function () {

    // Themes begin
    am4core.useTheme(am4themes_animated);
    // Themes end

    // Create chart instance
    var chart = am4core.create("chartdiv", am4charts.XYChart);
    //chart.colors.step = 2;
    chart.colors.list = [
        am4core.color("#0F69A3"),
        am4core.color("#98B8DA"),
        am4core.color("#ea7a71"),
        am4core.color("#fbd1c1")
    ];

    chart.numberFormatter.bigNumberPrefixes = [
        {"number": 1e+3, "suffix": "K"},
        {"number": 1e+6, "suffix": "Mi"},
        {"number": 1e+9, "suffix": "Bi"},
        {"number": 1e+12, "suffix": "Tri"},
        {"number": 1e+15, "suffix": "Qua"}
    ]
    chart.maskBullets = false;

    // Create axes
    var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.dataFields.category = "year";
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.renderer.minGridDistance = 20;
    categoryAxis.renderer.cellStartLocation = 0.2;
    categoryAxis.renderer.cellEndLocation = 0.8;
    categoryAxis.numberFormatter = new am4core.NumberFormatter();
    categoryAxis.numberFormatter.numberFormat = "#";
    categoryAxis.renderer.grid.template.disabled = true;

    var  valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.min = 0;
    valueAxis.numberFormatter.numberFormat = "#. a";
    valueAxis.renderer.grid.template.disabled = true;
    //valueAxis.title.text = "Expenditure (M)";

    let get_group = {
        "budget_revenue" : "revenue_group",
        "execution_revenue" : "revenue_group",
        "budget_expense" : "expense_group",
        "execution_expense" : "expense_group",
    }

    // Create series
    function createSeries(field, name, width, dx, label_dy = -15, label_color = "#000000") {
        var series = chart.series.push(new am4charts.ColumnSeries());
        series.dataFields.valueY = field;
        series.dataFields.categoryX = "year";
        series.name = name;
        series.clustered = false;
        series.dx = dx;
        series.columns.template.width = width;

        // Tooltip
        series.columns.template.tooltipText = `Ano: [bold]{year.formatNumber('#')}[/]
        Valor: [bold]{valueY.formatNumber('#,###')} ${country.currency}[/]
        ${name} de acordo com grupamento [bold,italic]{${get_group[field]}}`;

        // Label
        var bullet = series.bullets.push(new am4charts.LabelBullet());
        bullet.interactionsEnabled = true;
        bullet.dx = dx;
        bullet.dy = label_dy;
        bullet.fontSize = 11.5;
        bullet.label.verticalCenter = 'top';
        bullet.label.text = "[bold]{valueY.formatNumber('#.# a')}";
        bullet.label.fill = am4core.color(`${label_color}`);
        bullet.label.truncate = false;
    }

    chart.data = await new Promise((resolve, reject) => {
        $.get(url, function (data) {
            resolve(data)
        }).fail(function () {
            resolve([])
            console.error("Error on fetching budget basic info");
        });
    });

    // Add legend
    chart.legend = new am4charts.Legend();

    createSeries("budget_revenue", "Dotação Receita", 60, -20);
    createSeries("execution_revenue", "Execução Receita", 40, -20, 10, "#ffffff");
    createSeries("budget_expense", "Dotação Despesa", 60, 41);
    createSeries("execution_expense", "Execução Despesa", 40, 41, 10, "#ffffff");

}); // end am4core.ready()
