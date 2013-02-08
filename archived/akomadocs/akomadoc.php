<?php
	print("\nGenerating documentation....\n");
	print("Please wait, this will take a while\n");
	if (file_exists('newakoma.html')) {
	    $dom = new DOMDocument;
        $dom->preserveWhiteSpace = true;
        $dom->resolveExternals = true;
        $dom->loadHTMLFile('newakoma.html');
        $xpath = new DOMXpath($dom);
	}
	else
	{
	    exit('Failed to open newakoma.html.');
	}

	$divs = $xpath->query('//div[@class="componentTitle"]');
	
	foreach ($divs as $div){
	    
	    $html = '<html><head><link rel="stylesheet" href="docHtml.css" type="text/css" /></head><body>';
	   
	    $table = $div->nextSibling->nextSibling;
	    $xml = $table->ownerDocument->saveXML($table);
	    $html .= $xml;
	    
	    $html .= "</body></html>";
	 
	    $type = trim($div->firstChild->nodeValue);
	    echo $type, " and ";
	    $elementName = $div->firstChild->nextSibling->nodeValue;
	    echo $elementName, "\n";
	    
	    if ( $type === "Element")
	    {
	        $filename = $elementName."E.html";
	    }
	    else if ($type === "Element Group")
	    {
	        $filename = $elementName."EG.html";
	    }
	    else if ($type === "Attribute")
	    {
	    
	        $filename = "";
	    }
	    else if ($type === "Attribute Group")
	    {
	        $filename = $elementName."AG.html";
	    }
	    else if ($type === "Complex Type")
	    {
	        $filename = $elementName."CT.html";
	    }
	    else if ($type === "Simple Type")
	    {
	        $filename = $elementName."ST.html";
	    }
	    else
	    {
	        $filename = "";
	    }
	    if ($filename != "")
	    {
	        $fp = fopen('docs/'.$filename, 'w+');
	        fwrite($fp, $html);
	    }
	    else
	    {
	        echo "WTF", $type, "\n";
	    }
	   
	}
	
	echo "Finished \n";
?>
