import uk.ltd.filmlight.flapi.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

class GetScenes {

    public static void main( String[] args )
    {
        Connection conn = null;
        String host = "localhost";
        String dbpath = null;

        for( int i = 0; i < args.length; ++i )
        {
            if( args[i].equals("-h") )
            {
                if( i < (args.length-1) )
                {
                    host = args[++i];
                }
                else
                {
                    System.out.printf( "No hostname specified for -h argument\n" );
                    System.exit(1);
                }
            }
            else if( dbpath == null )
            {
                dbpath = args[i];
            }
        }

        if( dbpath == null )
        {
            System.out.printf( "No database host:job specified\n" );
            System.exit(1);
        }
            
        /* Parse host:job:folder string */
        String[] dbparts = dbpath.split(":");
        if( dbparts.length < 2 )
        {
            System.out.printf( "Invalid job name %s\n", dbpath );
            System.exit(1);
        }

        String dbhost = dbparts[0];
        String dbjob = dbparts[1];
        String dbfolder = null;
        for( int i = 2; i < dbparts.length; ++i )
        {
            if( dbfolder == null )
                dbfolder = dbparts[i];
            else
                dbfolder = dbfolder.concat(":").concat(dbparts[i]);
        }

        try
        {
            conn = new Connection(host);
            conn.connect();

            ArrayList<String> scenes;
            scenes = conn.JobManager.getScenes( dbhost, dbjob, dbfolder );

            System.out.printf( "Found %d scenes in job %s\n", scenes.size(), dbpath );
            for( String s : scenes )
                System.out.printf( "    %s:%s\n", dbjob, s );
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
