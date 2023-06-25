import uk.ltd.filmlight.flapi.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

class GetJobs {

    public static void main( String[] args )
    {
        Connection conn = null;
        String host = "localhost";
        String dbhost = null;

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
            else if( dbhost == null )
            {
                dbhost = args[i];
            }
        }

        if( dbhost == null )
        {
            System.out.printf( "No database host specified\n" );
            System.exit(1);
        }

        try
        {
            conn = new Connection(host);
            conn.connect();

            ArrayList<String> jobs = conn.JobManager.getJobs( dbhost );

            System.out.printf( "Found %d jobs on %s\n", jobs.size(), dbhost );
            for( String j : jobs )
                System.out.printf( "    %s:%s\n", dbhost, j );
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
