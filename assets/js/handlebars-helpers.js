function renderTemplate(template_selector, data={}, target_selector=null){
    var source = $(template_selector).html();
    var template = Handlebars.compile(source);
    var rendered = template(data);
    if(target_selector){
        $(target_selector).html(rendered);
    }
    return rendered;
}

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
    return (parseFloat(value)*100).toFixed(0)+"%";
});

Handlebars.registerHelper('parseFloat', function (value, decimals=2) {
    return parseFloat(value).toFixed(decimals);
});

Handlebars.registerHelper('parseInt', function (value) {
    return parseInt(value);
});

Handlebars.registerHelper("inc", function(value, options) {
    return parseInt(value) + 1;
});

Handlebars.registerHelper({
    eq: (v1, v2) => v1 === v2,
    ne: (v1, v2) => v1 !== v2,
    lt: (v1, v2) => v1 < v2,
    gt: (v1, v2) => v1 > v2,
    lte: (v1, v2) => v1 <= v2,
    gte: (v1, v2) => v1 >= v2,
    and() {
        return Array.prototype.every.call(arguments, Boolean);
    },
    or() {
        return Array.prototype.slice.call(arguments, 0, -1).some(Boolean);
    }
});