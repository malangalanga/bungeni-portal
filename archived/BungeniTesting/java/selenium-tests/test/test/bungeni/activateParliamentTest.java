package test.bungeni;

//~--- non-JDK imports --------------------------------------------------------

import com.thoughtworks.selenium.*;
import java.util.Properties;

public class activateParliamentTest extends SeleneseTestCase {

    @Override
    public void setUp() throws Exception {
        Properties props = CommonFunctions.getProps();
        setUp(props.getProperty("base_url"), props.getProperty("client_string"));
    }

    public void testActivateParliament() throws Exception {
        selenium.open("/");
        selenium.click("//ul[@id='portal-personaltools']/li/a/span");
        selenium.waitForPageToLoad("30000");
        selenium.type("login", "admin");
        selenium.type("password", "admin");
        selenium.click("actions.login");
        selenium.waitForPageToLoad("30000");
        selenium.click("link=administration");
        selenium.waitForPageToLoad("30000");
        selenium.click("//td[@id='portal-column-one']/div/dl/dd/ul/li/ul/li[1]/div/a/span");
        selenium.waitForPageToLoad("30000");
        for (int second = 0;; second++) {
			if (second >= 60) fail("timeout");
			try { if (selenium.isElementPresent("link=9th parliament 2002")) break; } catch (Exception e) {}
			Thread.sleep(1000);
		}
        selenium.click("link=9th parliament 2002");
        selenium.waitForPageToLoad("30000");
        selenium.click("//dl[@id='plone-contentmenu-workflow']/dt/a/span[2]");
        selenium.click("//a[@id='workflow-transition-activate-draft']/span");
        selenium.waitForPageToLoad("30000");
        selenium.click("form.actions.activate");
        selenium.waitForPageToLoad("30000");
    }
}
