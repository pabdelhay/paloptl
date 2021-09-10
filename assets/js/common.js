function sortByKey(array, key, direction='desc') {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        if(direction == 'desc'){
            return ((x > y) ? -1 : ((x < y) ? 1 : 0));
        } else {
            return ((x < y) ? -1 : ((x < y) ? 1 : 0));
        }
    });
}

function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}