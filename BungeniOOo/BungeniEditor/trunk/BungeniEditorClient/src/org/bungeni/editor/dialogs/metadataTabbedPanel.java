/*
 * metadataTabbedPanel.java
 *
 * Created on February 19, 2008, 5:04 PM
 */

package org.bungeni.editor.dialogs;

import java.awt.Color;
import java.awt.Component;
import java.awt.Font;
import java.awt.Point;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import javax.swing.BorderFactory;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JTable;
import javax.swing.JTree;
import javax.swing.Timer;
import javax.swing.border.BevelBorder;
import javax.swing.border.Border;
import javax.swing.border.LineBorder;
import javax.swing.table.TableCellRenderer;
import javax.swing.tree.TreeCellRenderer;
import org.bungeni.editor.dialogs.treetable.DocMetadataTreeTableModel;
import org.bungeni.editor.metadata.DocumentMetadataTableModel;
import org.bungeni.editor.dialogs.metadatapanel.DocumentMetadataTableModelLoad;
import org.bungeni.editor.dialogs.metadatapanel.SectionMetadataLoad;
import org.bungeni.ooo.BungenioOoHelper;
import org.bungeni.ooo.OOComponentHelper;
import org.apache.log4j.Logger;
import org.bungeni.editor.dialogs.treetable.sectionHive;
import org.jdesktop.swingx.JXTreeTable;


/**
 *
 * @author  john wesonga
 *
 */
public class metadataTabbedPanel extends javax.swing.JPanel {
    private OOComponentHelper ooDocument;
    //private DocumentMetadataTableModelLoad docMetadataTableModel;
    private DocumentMetadataTableModel docMetadataTableModel;
    private SectionMetadataLoad sectionMetadataTableModel;
    private JFrame parentFrame;
    private static org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(metadataTabbedPanel.class.getName());
    private Timer sectionNameTimer;
    private Timer sectionMetadataTimer;
    private String sectName;

    private DocMetadataTreeTableModel docMetadataTreeTable;
    /** Creates new form metadataTabbedPanel */
    public metadataTabbedPanel() {
        initComponents();
        
    }
    
     public metadataTabbedPanel(OOComponentHelper ooDocument, JFrame parentFrame){
         this.parentFrame=parentFrame;
         this.ooDocument=ooDocument;
         init();
     }
    
    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    // <editor-fold defaultstate="collapsed" desc=" Generated Code ">//GEN-BEGIN:initComponents
    private void initComponents() {
        jTabsContainer = new javax.swing.JTabbedPane();
        panelDocumentMetadata = new javax.swing.JPanel();
        scrollPaneDocumentMetadata = new javax.swing.JScrollPane();
        tableDocMetadata = new javax.swing.JTable();
        panelTreeTableDocumentMetadata = new javax.swing.JPanel();
        scrollPaneTreeTableDocumentMetadata = new javax.swing.JScrollPane();
        treeTableDocumentMetadata = new org.jdesktop.swingx.JXTreeTable();
        panelSectionMetadata = new javax.swing.JPanel();
        scrollPaneSectionMetadata = new javax.swing.JScrollPane();
        tableSectionMetadata = new javax.swing.JTable();
        lblSectionName = new javax.swing.JTextField();

        jTabsContainer.setTabLayoutPolicy(javax.swing.JTabbedPane.SCROLL_TAB_LAYOUT);
        jTabsContainer.setAutoscrolls(true);
        jTabsContainer.setFont(new java.awt.Font("Dialog", 0, 10));
        tableDocMetadata.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null},
                {null, null}
            },
            new String [] {
                "Title 1", "Title 2"
            }
        ));
        scrollPaneDocumentMetadata.setViewportView(tableDocMetadata);

        treeTableDocumentMetadata.setFont(new java.awt.Font("SansSerif", 0, 10));
        treeTableDocumentMetadata.setHorizontalScrollEnabled(true);
        scrollPaneTreeTableDocumentMetadata.setViewportView(treeTableDocumentMetadata);

        org.jdesktop.layout.GroupLayout panelTreeTableDocumentMetadataLayout = new org.jdesktop.layout.GroupLayout(panelTreeTableDocumentMetadata);
        panelTreeTableDocumentMetadata.setLayout(panelTreeTableDocumentMetadataLayout);
        panelTreeTableDocumentMetadataLayout.setHorizontalGroup(
            panelTreeTableDocumentMetadataLayout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(panelTreeTableDocumentMetadataLayout.createSequentialGroup()
                .addContainerGap()
                .add(scrollPaneTreeTableDocumentMetadata, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 257, Short.MAX_VALUE)
                .addContainerGap())
        );
        panelTreeTableDocumentMetadataLayout.setVerticalGroup(
            panelTreeTableDocumentMetadataLayout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(panelTreeTableDocumentMetadataLayout.createSequentialGroup()
                .addContainerGap(org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .add(scrollPaneTreeTableDocumentMetadata, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 163, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE))
        );

        org.jdesktop.layout.GroupLayout panelDocumentMetadataLayout = new org.jdesktop.layout.GroupLayout(panelDocumentMetadata);
        panelDocumentMetadata.setLayout(panelDocumentMetadataLayout);
        panelDocumentMetadataLayout.setHorizontalGroup(
            panelDocumentMetadataLayout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(panelTreeTableDocumentMetadata, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .add(panelDocumentMetadataLayout.createSequentialGroup()
                .add(12, 12, 12)
                .add(scrollPaneDocumentMetadata, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 257, Short.MAX_VALUE)
                .add(12, 12, 12))
        );
        panelDocumentMetadataLayout.setVerticalGroup(
            panelDocumentMetadataLayout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(panelDocumentMetadataLayout.createSequentialGroup()
                .add(scrollPaneDocumentMetadata, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 98, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .add(22, 22, 22)
                .add(panelTreeTableDocumentMetadata, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
        jTabsContainer.addTab("Document Metadata", panelDocumentMetadata);

        scrollPaneSectionMetadata.setFont(new java.awt.Font("Dialog", 0, 10));
        tableSectionMetadata.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {"METADATA", "METADATA_VALUE"},
                {null, null},
                {null, null},
                {null, null}
            },
            new String [] {
                "Title 1", "Title 2"
            }
        ));
        scrollPaneSectionMetadata.setViewportView(tableSectionMetadata);

        lblSectionName.setEditable(false);
        lblSectionName.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                lblSectionNameActionPerformed(evt);
            }
        });

        org.jdesktop.layout.GroupLayout panelSectionMetadataLayout = new org.jdesktop.layout.GroupLayout(panelSectionMetadata);
        panelSectionMetadata.setLayout(panelSectionMetadataLayout);
        panelSectionMetadataLayout.setHorizontalGroup(
            panelSectionMetadataLayout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(panelSectionMetadataLayout.createSequentialGroup()
                .addContainerGap()
                .add(panelSectionMetadataLayout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
                    .add(scrollPaneSectionMetadata, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 257, Short.MAX_VALUE)
                    .add(lblSectionName, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 170, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE))
                .addContainerGap(org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
        panelSectionMetadataLayout.setVerticalGroup(
            panelSectionMetadataLayout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(panelSectionMetadataLayout.createSequentialGroup()
                .addContainerGap()
                .add(lblSectionName, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(org.jdesktop.layout.LayoutStyle.RELATED)
                .add(scrollPaneSectionMetadata, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE, 119, org.jdesktop.layout.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(149, Short.MAX_VALUE))
        );
        jTabsContainer.addTab("Section Metadata", panelSectionMetadata);

        org.jdesktop.layout.GroupLayout layout = new org.jdesktop.layout.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(jTabsContainer, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 286, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(org.jdesktop.layout.GroupLayout.LEADING)
            .add(layout.createSequentialGroup()
                .add(jTabsContainer, org.jdesktop.layout.GroupLayout.DEFAULT_SIZE, 330, Short.MAX_VALUE)
                .addContainerGap())
        );
    }// </editor-fold>//GEN-END:initComponents

    private void lblSectionNameActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_lblSectionNameActionPerformed
// TODO add your handling code here:
    }//GEN-LAST:event_lblSectionNameActionPerformed
    
    
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JTabbedPane jTabsContainer;
    private javax.swing.JTextField lblSectionName;
    private javax.swing.JPanel panelDocumentMetadata;
    private javax.swing.JPanel panelSectionMetadata;
    private javax.swing.JPanel panelTreeTableDocumentMetadata;
    private javax.swing.JScrollPane scrollPaneDocumentMetadata;
    private javax.swing.JScrollPane scrollPaneSectionMetadata;
    private javax.swing.JScrollPane scrollPaneTreeTableDocumentMetadata;
    private javax.swing.JTable tableDocMetadata;
    private javax.swing.JTable tableSectionMetadata;
    private org.jdesktop.swingx.JXTreeTable treeTableDocumentMetadata;
    // End of variables declaration//GEN-END:variables
    
   
    private void init(){
        initComponents();
        initTableDocMetadata();
        initTreeTableDocMetadata();
        initTimers();
    }
    private void initTableDocMetadata(){
        //load metadata for the document
        // docMetadataTableModel = new DocumentMetadataTableModelLoad(ooDocument);
        // tableDocMetadata.setModel(docMetadataTableModel);  
        docMetadataTableModel = new DocumentMetadataTableModel(ooDocument);
        tableDocMetadata.setModel(docMetadataTableModel);
         this.tableDocMetadata.setFont(new Font("Tahoma", Font.PLAIN, 11));
    }
    
    private void initTreeTableDocMetadata(){
        sectionHive rootHive = new sectionHive("root");
      //  buildTree(rootHive);
        docMetadataTreeTable=new DocMetadataTreeTableModel(ooDocument, rootHive);
        treeTableDocumentMetadata.setTreeTableModel(docMetadataTreeTable);
        treeTableDocumentMetadata.setTreeCellRenderer(new treeTableDocumentMetadataCellRenderer());
        //this.treeTableDocumentMetadata.setFont(new Font("Tahoma", Font.PLAIN, 10));
        
    }
    
    private void updateSectionName(){
        String strSection="";
        strSection = ooDocument.currentSectionName();
        if(strSection.trim().length() == 0){
             lblSectionName.setText("No Section");
        }else{
             lblSectionName.setText(strSection);
        }
        
    }
    
    private void loadSectionMetadata(){
        String sectionName="";
        sectionName=ooDocument.currentSectionName();
        if(sectionName.trim().length()==0){
            log.debug("No section available");
            return;
        }else{
            sectionMetadataTableModel = new SectionMetadataLoad(ooDocument,sectionName);
            tableSectionMetadata.setModel(sectionMetadataTableModel);
            this.tableSectionMetadata.setFont(new Font("Tahoma", Font.PLAIN, 11));
        }
        
    }
    private synchronized void initTimers(){
       try{
              sectionNameTimer= new Timer(1000, new ActionListener() {
              public void actionPerformed(ActionEvent e) {
                 updateSectionName();
              }
           });
           sectionNameTimer.start();
           
          sectionMetadataTimer= new Timer(1000, new ActionListener() {
              public void actionPerformed(ActionEvent e) {
                loadSectionMetadata();
              }
           });
           sectionMetadataTimer.start();
           
       } catch(Exception e){
           log.error(e.getMessage());
       }
      
        
    }
    
    
    class tableDocMetadata {
        public String getToolTipText(MouseEvent e) {
         String tip=null;
         java.awt.Point p = e.getPoint();
         int rowIndex = rowAtPoint(p);
         int colIndex = columnAtPoint(p);
         tip = "This person's favorite sport to "
                           + "participate in is: "
                           + docMetadataTableModel.getValueAt(rowIndex, colIndex);
          return tip;
        }

        private int rowAtPoint(Point p) {
            return 0;
        }

        private int columnAtPoint(Point p) {
            return 0;
           
        }
    };
    
    public class treeTableDocumentMetadataCellRenderer extends JLabel implements TreeCellRenderer
    {
       
        
        public Component getTreeCellRendererComponent(JTree tree, Object value, boolean selected, boolean expanded, boolean leaf, int row, boolean hasFocus)
	{
            setForeground(Color.BLACK);
            setBorder(new javax.swing.border.LineBorder(Color.GRAY, 1));
            if(docMetadataTreeTable.getValueAt(value, 1).equals("")){
                setToolTipText(value.toString());
            }else{
                  setToolTipText(value.toString() + ":" + docMetadataTreeTable.getValueAt(value, 1));
            }
          

		if (selected)
		{
			Component vRenderPane = tree.getParent();
			if (vRenderPane != null)
			{
				JXTreeTable vTable = (JXTreeTable)vRenderPane.getParent();
				if (vTable != null)
				{
					if (vTable.hasFocus())
					{
						setForeground(Color.WHITE);
					}
				}
			}
		}
		setText(value.toString());
                
		return this;
        }
    
    
    
    }

  
/*
 private void btnShowDocMetadataPaneActionPerformed(java.awt.event.ActionEvent evt) {                                                       
// TODO add your handling code here:
           
           
            
            log.debug("Show Doc Metadata button clicked " + evt.getActionCommand());
            javax.swing.JFrame frame = new javax.swing.JFrame("Document Metadata Panel");
            
            panel = new org.bungeni.editor.dialogs.metadataTabbedPanel(this.ooDocument, frame);
            //panel.setOOoHelper(this.openofficeObject);
            frame.add(panel);
           
            //frame.setSize(243, 650);
            frame.setSize(320, 400);
            frame.setResizable(false);
            
            frame.setAlwaysOnTop(true);
            frame.setVisible(true);
            //position frame
            Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
            Dimension windowSize = frame.getSize();
            log.debug("screen size = "+ screenSize);
            log.debug("window size = "+ windowSize);
            
            int windowX = (screenSize.width  - frame.getWidth())/2;
            int windowY = (screenSize.height - frame.getHeight())/2;
            frame.setLocation(windowX, windowY);  // Don't use "f." inside constructor.
    }                                                      
*/


   

   
    
   
}
