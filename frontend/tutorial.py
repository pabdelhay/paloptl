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
        'text': _("The size of the rectangles is proportional to the volume of resources foreseen in "
                  "the budget of each rubric compared to the total budget. Click on the rectangles to refresh the "
                  "chart and understand the details of how resources are distributed within a specific rubric."),
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
        'element': '#chart-treemap',
        'title': _("Treemap data"),
        'text': _("When <b>moving the cursor over the rectangles</b>, informational balloons will appear, "
                  "specifying the absolute numbers of the allocation and the amount paid. Some countries report "
                  "how much of the allocation is relative to the budget for government functioning and "
                  "how much is relative to the investment budget. If available, these values will be displayed "
                  "in the informational balloons and on the \"Secondary Data\" card, to the left of the treemap."),
        'position': 'left'
    },
    {
        'element': '#historical-info',
        'title': _("Historic Series"),
        'text': _("The second view is the historical series. It shows the evolution in the amount of endowment "
                  "and amounts paid since 2016. The series is responsive to selections made in the treemap. "
                  "Thus, it is possible to quickly analyze the history of each of the rubrics listed on the platform."),
        'scrollTo': 'tooltip',
    },
    {
        'element': '#datatable-info',
        'title': _("Table"),
        'text': _("The last view is a table that summarizes all the information contained in the treemap. "
                  "It is possible to detail the information of a given rubric, by clicking on the corresponding line."),
        'scrollTo': 'tooltip',
    },
    {
        'element': '.expand-visualization',
        'title': _("Update visualizations"),
        'text': _("It is also possible to update the entire platform to present data referring to the rubric "
                  "selected in the table."),
    },
    {
        'element': '.download-link',
        'title': _("CSV"),
        'text': _("All data is available for download in .csv format."),
    }
]
