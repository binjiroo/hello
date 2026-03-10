import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import javafx.stage.Stage;

import java.awt.*;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.DataFlavor;

public class YouTubePlayerApp extends Application {
    private TextField urlField;
    private WebEngine webEngine;

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("YouTube Player");

        WebView webView = new WebView();
        webEngine = webView.getEngine();

        urlField = new TextField();
        urlField.setPromptText("Enter YouTube URL");
        urlField.setPrefWidth(600);

        Button playButton = new Button("Play");
        playButton.setOnAction(e -> playVideo());

        Button pasteButton = new Button("Paste");
        pasteButton.setOnAction(e -> pasteFromClipboard());

        Button clearButton = new Button("Clear");
        clearButton.setOnAction(e -> urlField.clear());

        HBox buttonBox = new HBox(10);
        buttonBox.getChildren().addAll(playButton, pasteButton, clearButton);

        VBox root = new VBox(10);
        root.getChildren().addAll(new Label("YouTube URL:"), urlField, buttonBox, webView);

        Scene scene = new Scene(root, 800, 600);
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    private void playVideo() {
        String url = urlField.getText();
        if (!url.isEmpty()) {
            webEngine.load(url);
        }
    }

    private void pasteFromClipboard() {
        Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
        try {
            String clipboardContent = (String) clipboard.getData(DataFlavor.stringFlavor);
            urlField.setText(clipboardContent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
