package visualisation;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridLayout;
import java.awt.Image;
import java.awt.event.AdjustmentEvent;
import java.awt.event.AdjustmentListener;
import java.awt.event.ComponentAdapter;
import java.awt.event.ComponentEvent;
import java.awt.image.BufferedImage;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollBar;
import javax.swing.SwingConstants;

import utility.game.player.PlayerAction;

public class ViewerWindow {

	// minimum dimensions of the window
	private static final int MIN_WINDOW_WIDTH = 700;
	private static final int MIN_WINDOW_HEIGHT = 500;

	// gap values for the info panel grid layout
	private static final int INFO_GAP_HORIZONTAL = 10;
	private static final int INFO_GAP_VERTICAL = 5;

	// paddings for board ratings
	private static final int BOARD_RATING_PADDING_HORIZONTAL = 32;
	private static final int BOARD_RATING_PADDING_VERTICAL = 32;

	// parent JFrame
	private final JFrame jFrame = new JFrame();

	// information labels
	private final JLabel roundLabel = new JLabel("-1");
	private final JLabel availableTimeLabel = new JLabel("-1");
	private final JLabel performedActionLabel = new JLabel("-1");
	private final JLabel requiredTimeLabel = new JLabel("-1");

	// panel to show different boards with specific ratings
	private final JPanel boardPanel = new JPanel();

	// scrollbar to scroll through the different rounds
	private final JScrollBar timelineScrollBar = new JScrollBar(JScrollBar.HORIZONTAL);

	// storing the board ratings added to the window
	private List<NamedImage> boardRatings = new ArrayList<>();

	/**
	 * Generates a new window and shows it.
	 */
	public ViewerWindow(Consumer<Integer> timelineChangeHandler) {

		// main panel of the whole window
		JPanel mainPanel = new JPanel();
		jFrame.add(mainPanel);
		mainPanel.setLayout(new BorderLayout());

		// panel to show boards with specific ratings
		mainPanel.add(boardPanel, BorderLayout.CENTER);

		// scroll bar to navigate the time line
		mainPanel.add(timelineScrollBar, BorderLayout.SOUTH);
		timelineScrollBar.setMinimum(0);
		timelineScrollBar.setMaximum(0);
		timelineScrollBar.setBlockIncrement(1);
		timelineScrollBar.addAdjustmentListener(new AdjustmentListener() {
			@Override
			public void adjustmentValueChanged(AdjustmentEvent event) {
				timelineChangeHandler.accept(event.getValue());
			}
		});

		// panel for info
		JPanel infoPanel = new JPanel();
		mainPanel.add(infoPanel, BorderLayout.EAST);
		infoPanel.setLayout(new BorderLayout());

		// panel for round specific information
		JPanel roundInfoPanel = new JPanel();
		infoPanel.add(roundInfoPanel, BorderLayout.NORTH);
		roundInfoPanel.setLayout(new GridLayout(0, 2, INFO_GAP_HORIZONTAL, INFO_GAP_VERTICAL));
		roundInfoPanel.add(new JLabel("gameround"));
		roundInfoPanel.add(roundLabel);
		roundInfoPanel.add(new JLabel("available time"));
		roundInfoPanel.add(availableTimeLabel);
		roundInfoPanel.add(new JLabel("performed action"));
		roundInfoPanel.add(performedActionLabel);
		roundInfoPanel.add(new JLabel("required time"));
		roundInfoPanel.add(requiredTimeLabel);

		// set minimum size of window
		jFrame.setMinimumSize(new Dimension(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT));

		// exit program when closing window
		jFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

		// redraw board ratings when window resize happens
		mainPanel.addComponentListener(new ComponentAdapter() {
			@Override
			public void componentResized(ComponentEvent e) {
				redrawBoardPanel();
			}
		});

		// show JFrame
		jFrame.setVisible(true);
	}

	/**
	 * Updates the displayed round in the window.
	 * 
	 * @param roundCounter
	 */
	public void setRoundCounter(final int roundCounter) {
		roundLabel.setText(Integer.toString(roundCounter));
	}

	/**
	 * Updates the displayed available time in the window.
	 * 
	 * @param availableTime
	 */
	public void setAvailableTime(final double availableTime) {
		availableTimeLabel.setText(String.format("%.4f", availableTime));
	}

	/**
	 * Updates the displayed performed action in the window.
	 * 
	 * @param performedAction
	 */
	public void setPerformedAction(final PlayerAction performedAction) {
		performedActionLabel.setText(performedAction.getName());
	}

	/**
	 * Updates the displayed required time in the window.
	 * 
	 * @param requiredTime
	 */
	public void setRequiredTime(final double requiredTime) {
		requiredTimeLabel.setText(String.format("%.4f", requiredTime));
	}

	/**
	 * Adds multiple {@link NamedImages} to the {@link ViewerWindow}.
	 * 
	 * @param namedImages
	 */
	public void updateBoardRatings(List<NamedImage> namedImages) {
		boardRatings = namedImages;
		redrawBoardPanel();
	}

	/**
	 * Internal function to handle a redraw of the board panel.
	 */
	private void redrawBoardPanel() {

		final int displayedBoards = boardRatings.size();

		if (displayedBoards > 0) {
			// recalculate grid layout
			final int xGridElements = (int) Math.ceil(Math.sqrt(displayedBoards));
			final int yGridElements = (int) Math.ceil(displayedBoards / xGridElements);
			boardPanel.setLayout(new GridLayout(yGridElements, xGridElements));

			// calculates max size in each dimension for board rating
			final float maxElementWidth = (boardPanel.getWidth() + BOARD_RATING_PADDING_HORIZONTAL) / xGridElements;
			final float maxElementHeight = (boardPanel.getHeight() + BOARD_RATING_PADDING_VERTICAL) / yGridElements;

			// update graphics
			boardPanel.removeAll();
			for (NamedImage namedImage : boardRatings) {

				// create new panel for Board rating
				JPanel singleBoardPanel = new JPanel();
				boardPanel.add(singleBoardPanel);

				// update layout
				singleBoardPanel.setLayout(new BorderLayout());
				JLabel imageTitle = new JLabel(namedImage.getName(), SwingConstants.CENTER);
				singleBoardPanel.add(imageTitle, BorderLayout.NORTH);
				BufferedImage image = namedImage.getImage();

				// scale and display image
				float scalingFactor = maxElementWidth / image.getWidth();
				if (image.getHeight() * scalingFactor > maxElementHeight)
					scalingFactor = maxElementHeight / image.getHeight();
				final int newWidth = (int) (image.getWidth() * scalingFactor);
				final int newHeight = (int) (image.getHeight() * scalingFactor);
				Image rescaledImage = image.getScaledInstance(newWidth, newHeight, Image.SCALE_FAST);
				ImageIcon imageIcon = new ImageIcon(rescaledImage);
				JLabel imageLabel = new JLabel(imageIcon);
				singleBoardPanel.add(imageLabel, BorderLayout.CENTER);
			}
		}

		boardPanel.repaint();
		boardPanel.revalidate();
	}

	/**
	 * Sets the max value for the time line, marking the highest round index the
	 * user may select.
	 * 
	 * @param maxValue
	 */
	public void setMaxTimelineValue(int maxValue) {
		this.timelineScrollBar.setMaximum(maxValue);
	}

	/**
	 * Externally shift the time line to a new value.
	 * 
	 * @param newValue the new value the timeline should be set to
	 */
	public void triggerTimlineChange(int newValue) {
		this.timelineScrollBar.setValue(newValue);
	}

}
