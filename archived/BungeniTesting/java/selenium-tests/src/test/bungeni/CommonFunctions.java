package test.bungeni;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Ashok Hariharan
 */
public class CommonFunctions {

    static public Properties getProps() {
       Properties props = null;
        try {
            String runtimePropsFile = System.getProperty("test.props");
            System.out.println("Runtime Properties File = " + runtimePropsFile);
            props = new Properties();
            props.load(new FileInputStream(new File(runtimePropsFile)));
        } catch (IOException ex) {
            Logger.getLogger(CommonFunctions.class.getName()).log(Level.SEVERE, null, ex);
        } return props;
        
    }

}
