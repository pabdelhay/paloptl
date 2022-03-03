from django.utils.translation import gettext_lazy as _

COUNTRY_DETAILS_TUTORIAL = [
    {
        'element': '.visualization-selector',
        'title': _("Visualizations"),
        'text': _("You can browse the budget through the following views: "
                  "<ul><li>Treemap</li><li>Historic Series</li><li>Table</li>"),
        'position': 'left'
    },
    {
        'element': '.budget-account-selector-row',
        'title': _("Query filters"),
        'text': _("Filters update the three visualizations synchronously. Choose here whether you want to see "
                  "<strong>revenue</strong> or <strong>expense</strong> data, <strong>classification type</strong> and "
                  "<strong>year</strong>."),
        'position': 'left'
    },
    {
        'element': '.budget-account-expenses',
        'title': _("Expense"),
        'text': _("Expense data is presented in two classification groups: <strong>Function</strong> "
                  "(government issues such as health and education) and <strong>Administrative bodies</strong> "
                  "(such as Ministries).")
    },
    {
        'element': '.budget-account-revenues',
        'title': _("Revenue"),
        'text': _("Revenues are presented by <strong>economic nature</strong>. This classification indicates the "
                  "actual event that led to the entry of the resource into public coffers (taxes or transfers, "
                  "for example)"),
        'position': 'bottom',
    },
    {
        'element': '.budget-selector',
        'title': _("Year"),
        'text': _("Data since 2016 is available on the platform."),
    },
    {
        'element': '.search-link',
        'title': _("Search"),
        'text': _("You can search for a specific expense or income in this icon."),
        'position': 'left'
    },
    {
        'element': '#chart-treemap',
        'title': _("Treemap"),
        'text': _("The size of the rectangles is proportional to the volume of resources foreseen in the budget of "
                  "each rubric compared to the total actually paid or received. Click on the rectangles to refresh "
                  "the chart and understand the details of how resources are distributed within a specific rubric."),
        'position': 'left'
    },
    {
        'element': '.treemap-legend-table',
        'title': _("Colors"),
        'text': _("The colors of the rectangles indicate the percentage (%) of the forecasted budget that was "
                  "actually spent or collected under the rubric. If this information is not available, "
                  "it will be grayed out."),
        'position': 'left'
    },
    {
        'element': '.secondary-info',
        'title': _("Secondary data"),
        'text': _("Some countries make available how much of the budget is directed towards maintenance of "
                  "government services (current budget) investments (investment budget). If available, "
                  "this information will show here."),
        'position': 'right'
    },
    {
        'element': '#historical-info',
        'title': _("Historic Series"),
        'text': _("It shows the evolution of revenues and expenses since 2016. This chart is responsive to the "
                  "queries defined in the treemap. Thus, it is possible to quickly analyze the history of "
                  "each item listed on the platform."),
        'scrollTo': 'tooltip',
    },
    {
        'element': '#datatable-info',
        'title': _("Table"),
        'text': _("It summarizes all data presented in the treemap. Breakdown the information of a given item by "
                  "clicking on it."),
        'scrollTo': 'tooltip',
    },
    {
        'element': '.expand-visualization',
        'title': _("Update visualizations"),
        'text': _("Click here to update all charts in order to display data of the item you are interested in."),
    },
    {
        'element': '.download-link',
        'title': _("CSV"),
        'text': _("All data is available for download in .csv format."),
    }
]

INDEX_DIMENSIONS = [
    {
        'element': '.header-open_data',
        'title': _("Open data"),
        'position': 'bottom',
        'text': _("Data must be <strong>complete, primary</strong> (collected from source, made available by the "
                   "institution that generates it), <strong>accessible</strong> (available online), "
                   "<strong>non-discriminatory</strong> (anyone can access it, with no need for registration "
                   "or identification), <strong>updated</strong> (defined according to the data type), "
                   "in <strong>machine-processable and nonproprietary</strong> format (.csv for example), and under "
                   "<strong>free license</strong> (not patented or copyrighted).")
    },
    {
        'element': '.header-score_reports',
        'title': _("Budget Reports"),
        'position': 'bottom',
        'text': _("Accesses whether reports relating to the budget implementation cycle are "
                   "<strong>produced and published</strong> in a timely manner. The reports evaluated are "
                   "the <strong>Enacted Budget, the Execution Reports and the Year-End Report</strong> "
                   "(or General State Accounts. See the methodology to understand more about "
                   "the scoring logic in this dimension.")
    },
    {
        'element': '.header-data_quality',
        'title': _("Information Quality"),
        'position': 'bottom',
        'text': _("This dimension assesses whether the country presents the <strong>planned and "
                   "executed budget</strong> according to the following classifications: <strong>revenue by "
                   "economic nature</strong> (source of the income, such as taxes and transfers), "
                   "<strong>expenditures by administrative classification</strong> (such as administrative bodies) "
                   "or by <strong>functional classification</strong> (such as health and education.")
    }
]
