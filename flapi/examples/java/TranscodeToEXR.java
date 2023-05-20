import uk.ltd.filmlight.flapi.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

class TranscodeToEXR {

    public static void main( String[] args )
    {
        Connection conn = null;
        String dstpath = null;
        String seqpath = null;
        Long startFrame = null, endFrame = null;

        /* Parse arguments */
        if( args.length < 2 )
        {
            System.out.printf( "Usage: <destination directory> <source movie> [<start frame> <end frame>]\n" );
            System.exit(1);
        }

        dstpath = args[0];
        seqpath = args[1];
        if( args.length >= 4 )
        {
            startFrame = Long.parseLong( args[2], 10 );
            endFrame = Long.parseLong( args[3], 10 );
        }

        try
        {
            /* Launch FLAPI process */
            conn = new Connection();
            conn.launch();

            System.out.printf( "Starting transcode of %s\n", seqpath );
           
            /*****************************************************/
            /* Find SequenceDescriptor for the source file */

            ArrayList<SequenceDescriptor> seqDescs;
            seqDescs = conn.SequenceDescriptor.getForTemplate( seqpath, startFrame, endFrame );

            if( seqDescs.size() == 0 )
            {
                System.out.printf( "Could not find sequence for %s\n", seqpath );
                System.exit(1);
            }
            
            SequenceDescriptor seqDesc = seqDescs.get(0);

            /*****************************************************/
            /* Define a format that matches the width/height of the sequence */

            Long fmtWidth = seqDesc.getWidth();
            Long fmtHeight = seqDesc.getHeight();
            String fmtName = String.format( "Netflix %dx%d", fmtWidth, fmtHeight );
            
            FormatSet globalFormats = conn.FormatSet.globalFormats();
            Format f = globalFormats.addFormat( fmtName, "Created by FLAPI for transcode", fmtWidth, fmtHeight, 1.0 );

            /*****************************************************/
            /* Create a temporary (in-memory) scene to contain the sequence */

            NewSceneOptions options = new NewSceneOptions();
            options.format = fmtName;
            options.colourspace = "ACES_lin";
            options.frame_rate = 24.0;
            options.field_order = Constants.FIELDORDER_PROGRESSIVE;

            Scene scene = conn.Scene.temporaryScene( options );

            /*****************************************************/
            /* Insert the SequenceDescriptor into the Scene */

            scene.startDelta( "Insert Sequence" );

            Shot newShot = 
                scene.insertSequence( 
                    seqDesc, 
                    Constants.INSERT_END,
                    null, /* relativeTo shot (not required as we're inserting at the end of the scene) */
                    null, /* automatically determine input colourspace */
                    fmtName  /* use new format we have defined */
                );


            /* NOTE: 
             * If you want to set any decode parameters, you can use Shot.setDecodeParameters() on newShot
             * If you want to set any metadata, you can use Shot.setMetadata()
             */

            newShot.release(); /* release shot object as we're finished with it */

            scene.endDelta();

            /*****************************************************/
            /* Create a RenderSetup to transcode this scene to EXR */

            RenderDeliverable exrDeliverable = new RenderDeliverable();

            exrDeliverable.Name = "Render to EXR";
            exrDeliverable.FileType = "EXR";

            exrDeliverable.OutputDirectory = dstpath;
            exrDeliverable.FileNamePrefix = "render_";
            exrDeliverable.FileNamePostfix = "";
            exrDeliverable.FileNameExtension = ".exr";
            exrDeliverable.FileNameNumDigits = 7L;
            exrDeliverable.FileNameNumber = Constants.RENDER_FRAMENUM_SHOT_FRAME;
            
            exrDeliverable.RenderFormat = fmtName; /* use name of new format we have defined */
            exrDeliverable.RenderColourSpace = "ACES_lin";
            
            RenderSetup rs = conn.RenderSetup.create();
            rs.setScene( scene );
            rs.addDeliverable( exrDeliverable );

            /*****************************************************/
            /* Get the RenderProcessor and start executing this RenderSetup */

            RenderProcessor processor = conn.RenderProcessor.get();
            
            System.out.printf( "Render Start\n" );
            processor.start( rs );

            /* Wait for processor to complete */
            RenderStatus progress;
            while( true )
            {
                progress = processor.getProgress();
                if( progress.Status.equals(Constants.OPSTATUS_DONE) )
                    break;

                System.out.printf( 
                    "Render Status: %s Frames: %d/%d\n", 
                    progress.Status,
                    progress.Complete,
                    progress.Total
                );

                try
                {
                    Thread.sleep( 1000 /* ms */ );
                }
                catch( InterruptedException iex )
                {
                }
            }

            ArrayList<RenderProcessorLogItem> logs = processor.getLog();
            for( RenderProcessorLogItem li : logs )
                System.out.printf( "%s : %s", li.Message, li.Detail );

            if( progress.Error != null )
                System.out.printf( "Render Failed: %s\n", progress.Error );
            else
                System.out.printf( "Render Complete\n" );

            scene.closeScene();
        }
        catch( FLAPIException ex )
        {
            System.out.printf( "Error: %s\n", ex.getMessage() );
            System.exit(1);
        }
        finally
        {
            if( conn != null )
                conn.close();
        }
    }
}
