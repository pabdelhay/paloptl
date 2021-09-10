<h1><b>Gsearch</b></h1>

<h2>Gsearch is a jquery searchable plugin which helps to search text on the webpage in a easy way.</h2>

<h3>Tiny, fast jQuery plugin to search text through elements as you type. This plugin is created and maintained 
   by Gurudath BN ( Github ). </h3>

<h2><b>Features</b></h2>
    
  Lightweight. This plugin is only ~3.8kB minified and gzipped!
	
  Fast. This plugin is optimized for fast, lagless searching even through large element sets.
	
  Search types. This plugin provides search text ! Fuzzy matching, case insensitive also.
	
  Custom show/hide. You can define custom functions for showing and hiding the elements while searching.
	
  Provide a icon on hover textfield appear to search text , so it wont occupy space on page.
	
  Search anything. This plugin isn't restricted to use on tables, any set of elements that has 'rows' 
   with 'columns' inside them can be used.

   
<h2><b>Demo</b></h2>

<b>Click here to view a demo of this plugin in action</b>

<a src='https://jsfiddle.net/gurudath/k197zu3a/7/'>https://jsfiddle.net/gurudath/k197zu3a/7/</a>

<h2><b>Getting started</b></h2>

<b>Basic usage</b>

After downloading this plugin, include it in your HTML file after loading jQuery:

<script src="https://code.jquery.com/jquery-migrate-1.2.1.min.js"></script>
<script src="gsearch.js"></script>

<b>Example usage</b>

This example uses the configurations shown above to customize the plugin:

 <p>$(document).ready(function () {</p>
     <p> &nbsp; &nbsp; &nbsp; &nbsp;$('#update_stiky_search').GSearch({</p>
    <p>    &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;   update_at: 'update_stiky_search',</p>
      <p>   &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;     margin_top: '100px',</p>
    <p>     &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;    background_color: '#01A9DB',</p>
     <p>     &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;   highlight_class: 'highlight',</p>
     <p>      &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;  content_main: $('.main-content')</p>
      <p>    &nbsp; &nbsp; &nbsp; &nbsp; });</p>
  <p>});</p>


Please feel free to submit any issues or pull requests, they are more then welcome. When submitting an issue, please specify the version number and describe the issue in detail so that it can be solved as soon as possible!

License

Copyright (c) 2014 - Licensed under the MIT license.
/*
highlight v3  !! Modified by Jon Raasch (http://jonraasch.com) to fix IE6 bug !!
Highlights arbitrary terms.
<http://johannburkard.de/blog/programming/javascript/highlight-javascript-text-higlighting-jquery-plugin.html>
MIT license.
Johann Burkard
<http://johannburkard.de>
<mailto:jb@eaio.com>
*/
