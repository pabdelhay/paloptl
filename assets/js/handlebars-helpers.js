Handlebars.registerHelper('formatCurrency', function (value) {
    if(!value){
        return "-"
    }
    var formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        currencyDisplay: 'code',
    });

    var number_without_sign = formatter.format(value).replace(/[a-z]{3}/i, "").trim();
    return number_without_sign;
});

Handlebars.registerHelper('formatPercent', function (value) {
    if(!value){
        return "-"
    }
    return (parseFloat(value)*100).toFixed(2)+"%";
});