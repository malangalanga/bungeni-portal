<?php
	print("\nFixing Links....\n");
	print("Please wait, this will take a while\n");
	if (file_exists('akomantoso100.html')) {
	    $dom = new DOMDocument;
        $dom->preserveWhiteSpace = true;
        $dom->resolveExternals = true;
        $dom->loadHTMLFile('akomantoso100.html');
        $xpath = new DOMXpath($dom);
	}
	else
	{
	    exit('Failed to open akomantoso100.html.');
	}

	$divs = $xpath->query('//div[@class="componentTitle"]');
	foreach ($divs as $div){
	    $anchor = $div->previousSibling;
	    //$xml = $anchor->ownerDocument->saveXML($anchor);
	    $id = $anchor->getAttribute("id");
	   // echo $id, "\n";
	   $type = trim($div->firstChild->nodeValue);
	   $elementName = $div->firstChild->nextSibling->nodeValue;
	   
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
	    //echo $id, " => ", $elementName, " => ",$filename ,"\n";
	    $map[$id] = $filename;
	}	
	$mapElements = $dom->getElementsByTagName( "area" );
	foreach ($mapElements as $mapElement)
	{
	    $link = $mapElement->getAttribute("href");
	    $anchorlink = substr($link, 19);
	    $reallink = $map[$anchorlink];
	    //echo $anchorlink, " replaced by ", $reallink, "\n";
	    $mapElement->setAttribute('href',$reallink);
	}
	$aElements = $dom->getElementsByTagName( "a" );
	foreach ($aElements as $aElement)
	{
	    $link = $aElement->getAttribute("href");
	    $anchorlink = substr($link, 19);
	    $reallink = $map[$anchorlink];
	    //echo $anchorlink, " replaced by ", $reallink, "\n";
	    $aElement->setAttribute('href',$reallink);
	    $aElement->removeAttribute("onclick");
	    $aElement->removeAttribute("target");
	    $aElement->removeAttribute("title");
	}
	$dom->save('newakoma.html');
	echo "Finished \n";
?>
